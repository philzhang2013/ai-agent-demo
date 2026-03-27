"""
聊天端点
支持 SSE 流式输出
"""
import json
import logging
import uuid
from fastapi import APIRouter, HTTPException, Depends
from sse_starlette.sse import EventSourceResponse

from app.models import ChatRequest, ChatResponse
from app.agent.base import Agent, create_llm_client
from app.config import get_settings
from app.db.repositories import MessageRepository, SessionRepository, MemorySummaryRepository
from app.memory.manager import MemoryManager
from app.memory.config import create_smart_memory_manager
from app.memory.smart_memory_manager import SmartMemoryManager
from app.memory.importance_scorer import ImportanceScorer

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)


def is_valid_uuid(value: str) -> bool:
    """检查字符串是否是有效的 UUID"""
    try:
        uuid.UUID(value)
        return True
    except (ValueError, TypeError):
        return False


def get_agent() -> Agent:
    """获取 Agent 实例（依赖注入）"""
    settings = get_settings()
    agent = Agent(
        provider=settings.llm_provider,
        api_key=settings.kimi_api_key if settings.llm_provider == "kimi" else settings.zhipuai_api_key,
        model=settings.kimi_model if settings.llm_provider == "kimi" else settings.zhipuai_model,
        max_iterations=settings.max_iterations
    )
    logger.debug(f"[创建 Agent] provider={settings.llm_provider}, model={settings.kimi_model if settings.llm_provider == 'kimi' else settings.zhipuai_model}, max_iterations={settings.max_iterations}")
    return agent


def get_agent() -> Agent:
    """获取 Agent 实例（依赖注入）"""
    settings = get_settings()
    return Agent(
        provider=settings.llm_provider,
        api_key=settings.kimi_api_key if settings.llm_provider == "kimi" else settings.zhipuai_api_key,
        model=settings.kimi_model if settings.llm_provider == "kimi" else settings.zhipuai_model,
        max_iterations=settings.max_iterations
    )


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, agent: Agent = Depends(get_agent)):
    """非流式聊天端点"""
    session_id = request.session_id or "default-session"
    logger.info(f"[POST /api/chat] session_id={session_id}, message={request.message[:50]}{'...' if len(request.message) > 50 else ''}")

    try:
        response = await agent.process_message(request.message)

        logger.info(f"[POST /api/chat] 响应成功, session_id={session_id}, content={response.content[:50]}{'...' if response.content and len(response.content) > 50 else ''}")

        return ChatResponse(
            response=response.content,
            session_id=session_id
        )
    except Exception as e:
        logger.error(f"[POST /api/chat] 错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(request: ChatRequest, agent: Agent = Depends(get_agent)):
    """流式聊天端点（SSE）"""
    session_id = request.session_id or "default"
    user_message = request.message
    logger.info(f"[POST /api/chat/stream] session_id={session_id}, message={user_message[:50]}{'...' if len(user_message) > 50 else ''}")

    # 初始化仓库和 MemoryManager
    message_repo = MessageRepository()
    session_repo = SessionRepository()
    summary_repo = MemorySummaryRepository()
    from app.db.repositories import ImportanceScoreRepository

    # 初始化 MemoryManager（需要 LLM 客户端）
    settings = get_settings()
    from app.agent.base import create_llm_client
    llm_client = create_llm_client(
        settings.llm_provider,
        settings.kimi_api_key if settings.llm_provider == "kimi" else settings.zhipuai_api_key
    )
    memory_model = settings.kimi_model if settings.llm_provider == "kimi" else settings.zhipuai_model
    memory_manager = MemoryManager(message_repo, summary_repo, llm_client, memory_model)

    # 初始化 SmartMemoryManager（用于自动生成 topic_tag 和 embedding）
    smart_manager = await create_smart_memory_manager()

    async def event_generator():
        """生成 SSE 事件"""
        event_count = 0
        reasoning_buffer = []
        content_buffer = []

        try:
            # 首先保存用户消息（这样消息数才准确）
            saved_user_message_id = None
            if is_valid_uuid(session_id):
                try:
                    user_msg = await message_repo.create(
                        session_id=session_id,
                        role="user",
                        content=user_message
                    )
                    saved_user_message_id = user_msg.id
                    logger.debug(f"[POST /api/chat/stream] 用户消息已保存, session_id={session_id}, message_id={saved_user_message_id}")

                    # 自动生成 topic_tag 和 embedding（异步，不阻塞主流程）
                    try:
                        await smart_manager.process_message({
                            "id": saved_user_message_id,
                            "session_id": session_id,
                            "content": user_message,
                            "created_at": user_msg.created_at
                        })
                        logger.debug(f"[POST /api/chat/stream] 用户消息已处理（topic_tag, embedding）, session_id={session_id}")
                    except Exception as smart_error:
                        logger.warning(f"[POST /api/chat/stream] 智能记忆处理失败（用户消息）: {smart_error}")

                    # 检查是否需要生成摘要
                    try:
                        should_summarize = await memory_manager.should_summarize(session_id)
                        if should_summarize:
                            logger.info(f"[POST /api/chat/stream] 触发摘要生成, session_id={session_id}")

                            # 获取所有消息生成摘要
                            all_messages = await message_repo.find_by_session_id(session_id)
                            messages_for_summary = [
                                {"role": msg.role, "content": msg.content}
                                for msg in all_messages
                            ]

                            # 生成摘要
                            summary_content = await memory_manager.generate_summary(messages_for_summary)

                            if summary_content:
                                # 保存/更新摘要
                                await summary_repo.create(
                                    session_id=session_id,
                                    content=summary_content,
                                    message_count=len(all_messages)
                                )
                                logger.info(f"[POST /api/chat/stream] 摘要已保存, session_id={session_id}, message_count={len(all_messages)}")
                            else:
                                logger.warning(f"[POST /api/chat/stream] 摘要生成失败或为空, session_id={session_id}")
                    except Exception as summary_error:
                        # 摘要生成失败不阻断主流程
                        logger.error(f"[POST /api/chat/stream] 摘要生成异常: {summary_error}", exc_info=True)

                except Exception as db_error:
                    logger.error(f"[POST /api/chat/stream] 保存用户消息失败: {db_error}", exc_info=True)

            # 使用 MemoryManager 构建上下文
            if is_valid_uuid(session_id):
                try:
                    context_messages = await memory_manager.get_context(session_id)
                    # 上下文最后一个消息是用户刚发的，需要替换成当前消息
                    # 移除最后一个用户消息，添加当前消息
                    if context_messages and context_messages[-1].get("role") == "user":
                        context_messages = context_messages[:-1]
                    context_messages.append({"role": "user", "content": user_message})
                    logger.debug(f"[POST /api/chat/stream] 使用记忆上下文, session_id={session_id}, context_length={len(context_messages)}")
                except Exception as ctx_error:
                    logger.error(f"[POST /api/chat/stream] 获取上下文失败: {ctx_error}", exc_info=True)
                    # 失败时使用原始消息
                    context_messages = [{"role": "user", "content": user_message}]
            else:
                context_messages = [{"role": "user", "content": user_message}]

            # 使用上下文调用 Agent 的流式处理方法
            async for event in agent.process_message_stream_with_context(context_messages):
                event_count += 1

                # 根据事件类型发送不同的 SSE 事件
                if event["event"] == "reasoning":
                    reasoning_buffer.append(event["content"])
                    yield {
                        "event": "reasoning",
                        "data": json.dumps({"content": event["content"]}, ensure_ascii=False)
                    }
                elif event["event"] == "content":
                    content_buffer.append(event["content"])
                    yield {
                        "event": "token",
                        "data": json.dumps({"content": event["content"]}, ensure_ascii=False)
                    }
                elif event["event"] == "tool_call":
                    yield {
                        "event": "tool_call",
                        "data": json.dumps({
                            "tool_calls": event["tool_calls"]
                        }, ensure_ascii=False)
                    }
                elif event["event"] == "tool_result":
                    yield {
                        "event": "tool_result",
                        "data": json.dumps({
                            "tool": event["tool"],
                            "result": event["result"]
                        }, ensure_ascii=False)
                    }
                elif event["event"] == "tool_error":
                    yield {
                        "event": "tool_error",
                        "data": json.dumps({
                            "tool": event["tool"],
                            "error": event["error"]
                        }, ensure_ascii=False)
                    }
                elif event["event"] == "error":
                    # 转发错误事件到前端
                    error_msg = event.get("error", "未知错误")
                    logger.warning(f"[POST /api/chat/stream] 收到错误事件: {error_msg}")
                    yield {
                        "event": "error",
                        "data": json.dumps({"error": error_msg}, ensure_ascii=False)
                    }
                    # 错误事件后直接结束，不继续处理
                    return

            # 流式响应完成，保存助手回复到数据库
            full_content = "".join(reasoning_buffer) + "".join(content_buffer)

            if is_valid_uuid(session_id):
                try:
                    saved_assistant_message_id = None
                    if full_content:
                        assistant_msg = await message_repo.create(
                            session_id=session_id,
                            role="assistant",
                            content=full_content
                        )
                        saved_assistant_message_id = assistant_msg.id
                        logger.debug(f"[POST /api/chat/stream] 助手回复已保存, session_id={session_id}, message_id={saved_assistant_message_id}")

                        # 自动生成 topic_tag 和 embedding（异步，不阻塞主流程）
                        try:
                            await smart_manager.process_message({
                                "id": saved_assistant_message_id,
                                "session_id": session_id,
                                "content": full_content,
                                "created_at": assistant_msg.created_at
                            })
                            logger.debug(f"[POST /api/chat/stream] 助手消息已处理（topic_tag, embedding）, session_id={session_id}")
                        except Exception as smart_error:
                            logger.warning(f"[POST /api/chat/stream] 智能记忆处理失败（助手消息）: {smart_error}")

                        # 检查是否需要创建主题段（当消息数达到阈值时）
                        try:
                            all_messages = await message_repo.find_by_session_id(session_id)
                            if len(all_messages) >= 6:  # 每轮对话有 2 条消息（用户+助手），3 轮后创建主题段
                                await smart_manager.create_topic_segments(
                                    session_id=session_id,
                                    messages=[
                                        {
                                            "id": msg.id,
                                            "content": msg.content,
                                            "created_at": msg.created_at,
                                            "role": msg.role
                                        }
                                        for msg in all_messages
                                    ]
                                )
                                logger.info(f"[POST /api/chat/stream] 主题段已创建, session_id={session_id}, message_count={len(all_messages)}")
                        except Exception as segment_error:
                            logger.warning(f"[POST /api/chat/stream] 主题段创建失败: {segment_error}")

                    # 更新会话时间戳
                    await session_repo.update(session_id)
                    logger.debug(f"[POST /api/chat/stream] 会话时间戳已更新, session_id={session_id}")

                except Exception as db_error:
                    logger.error(f"[POST /api/chat/stream] 数据库保存失败: {db_error}", exc_info=True)

            # 发送完成事件
            logger.info(f"[POST /api/chat/stream] 流式完成, session_id={session_id}, events={event_count}")
            yield {
                "event": "done",
                "data": json.dumps({"session_id": session_id}, ensure_ascii=False)
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"[POST /api/chat/stream] 错误: {error_msg}", exc_info=True)

            if "1113" in error_msg or "余额不足" in error_msg:
                friendly_error = "API 余额不足，请联系管理员充值"
            elif "429" in error_msg or "繁忙" in error_msg or "overloaded" in error_msg:
                friendly_error = "Kimi 服务繁忙，请稍后重试"
            elif "401" in error_msg:
                friendly_error = "Kimi API 认证失败，请检查 API Key"
            elif "403" in error_msg:
                friendly_error = "Kimi API 权限不足，请检查账号状态"
            else:
                friendly_error = f"服务暂时不可用: {error_msg}"

            logger.warning(f"[POST /api/chat/stream] 友好错误信息: {friendly_error}")

            yield {
                "event": "error",
                "data": json.dumps({"error": friendly_error}, ensure_ascii=False)
            }

    return EventSourceResponse(event_generator())


@router.post("/{session_id}/analyze")
async def analyze_session_memory(
    session_id: str,
    smart_manager: SmartMemoryManager = Depends(create_smart_memory_manager)
):
    """
    分析会话记忆，生成主题段和重要性评分

    Args:
        session_id: 会话 ID

    Returns:
        分析结果，包括主题段、重要性统计等
    """
    logger.info(f"[POST /api/chat/{session_id}/analyze] 开始分析会话记忆")

    try:
        # 验证 session_id
        if not is_valid_uuid(session_id):
            raise HTTPException(status_code=400, detail="无效的会话 ID")

        # 获取会话消息
        message_repo = MessageRepository()
        messages = await message_repo.find_by_session_id(session_id)

        if not messages:
            return {
                "session_id": session_id,
                "message_count": 0,
                "segments": [],
                "average_importance": 0.0,
                "topics": []
            }

        # 转换为字典列表
        message_dicts = [
            {
                "id": msg.id,
                "content": msg.content,
                "created_at": msg.created_at,
                "role": msg.role
            }
            for msg in messages
        ]

        # 处理每条消息的重要性评分
        for msg in message_dicts:
            await smart_manager.process_message(msg)

        # 创建主题段
        segments = await smart_manager.create_topic_segments(
            session_id=session_id,
            messages=message_dicts
        )

        # 计算整体重要性
        avg_importance = smart_manager.calculate_session_importance(message_dicts)

        # 获取高重要性消息
        high_importance = await smart_manager.get_high_importance_messages(
            session_id=session_id,
            threshold=0.7,
            limit=10
        )

        logger.info(f"[POST /api/chat/{session_id}/analyze] 分析完成, "
                   f"消息数={len(messages)}, 主题段数={len(segments)}")

        return {
            "session_id": session_id,
            "message_count": len(messages),
            "average_importance": avg_importance,
            "segment_count": len(segments),
            "segments": [
                {
                    "topic_name": seg.topic_name,
                    "message_count": seg.message_count,
                    "importance_score": seg.importance_score,
                    "summary": seg.summary[:200] if seg.summary else ""
                }
                for seg in segments
            ],
            "topics": list(set(seg.topic_name for seg in segments)),
            "high_importance_messages": [
                {"id": msg[0], "score": msg[1], "content": msg[2][:100]}
                for msg in high_importance
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[POST /api/chat/{session_id}/analyze] 错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/{session_id}/memory")
async def get_session_memory(
    session_id: str,
    query: str = None,
    limit: int = 5,
    smart_manager: SmartMemoryManager = Depends(create_smart_memory_manager)
):
    """
    获取会话记忆，支持语义搜索

    Args:
        session_id: 会话 ID
        query: 搜索查询（可选，如果不提供则返回所有主题段）
        limit: 返回结果数量限制

    Returns:
        主题段列表或搜索结果
    """
    logger.info(f"[GET /api/chat/{session_id}/memory] query={query}, limit={limit}")

    try:
        # 验证 session_id
        if not is_valid_uuid(session_id):
            raise HTTPException(status_code=400, detail="无效的会话 ID")

        if query:
            # 语义搜索
            results = await smart_manager.semantic_search(
                session_id=session_id,
                query=query,
                limit=limit
            )
            return {
                "session_id": session_id,
                "query": query,
                "results": [
                    {
                        "topic_name": seg.topic_name,
                        "summary": seg.summary,
                        "importance_score": seg.importance_score,
                        "message_count": seg.message_count
                    }
                    for seg in results
                ]
            }
        else:
            # 获取所有主题段
            segments = await smart_manager.segment_repo.find_by_session_id(session_id)
            return {
                "session_id": session_id,
                "segments": [
                    {
                        "topic_name": seg.topic_name,
                        "summary": seg.summary_content,
                        "importance_score": seg.importance_score,
                        "message_count": seg.message_count
                    }
                    for seg in segments
                ]
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[GET /api/chat/{session_id}/memory] 错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取记忆失败: {str(e)}")
