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
        provider="zhipuai",
        api_key=settings.zhipuai_api_key,
        model=settings.zhipuai_model,
        max_iterations=settings.max_iterations
    )
    logger.debug(f"[创建 Agent] model={settings.zhipuai_model}, max_iterations={settings.max_iterations}")
    return agent


def get_agent() -> Agent:
    """获取 Agent 实例（依赖注入）"""
    settings = get_settings()
    return Agent(
        provider="zhipuai",
        api_key=settings.zhipuai_api_key,
        model=settings.zhipuai_model,
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

    # 初始化 MemoryManager（需要 LLM 客户端）
    settings = get_settings()
    from app.agent.base import create_llm_client
    llm_client = create_llm_client("zhipuai", settings.zhipuai_api_key)
    memory_manager = MemoryManager(message_repo, summary_repo, llm_client, settings.zhipuai_model)

    async def event_generator():
        """生成 SSE 事件"""
        event_count = 0
        reasoning_buffer = []
        content_buffer = []

        try:
            # 首先保存用户消息（这样消息数才准确）
            if is_valid_uuid(session_id):
                try:
                    await message_repo.create(
                        session_id=session_id,
                        role="user",
                        content=user_message
                    )
                    logger.debug(f"[POST /api/chat/stream] 用户消息已保存, session_id={session_id}")

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

            # 流式响应完成，保存助手回复到数据库
            full_content = "".join(reasoning_buffer) + "".join(content_buffer)

            if is_valid_uuid(session_id):
                try:
                    if full_content:
                        await message_repo.create(
                            session_id=session_id,
                            role="assistant",
                            content=full_content
                        )
                        logger.debug(f"[POST /api/chat/stream] 助手回复已保存, session_id={session_id}")

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
            elif "429" in error_msg or "频率" in error_msg:
                friendly_error = "请求过于频繁，请稍后再试"
            elif "401" in error_msg or "403" in error_msg:
                friendly_error = "API 认证失败，请检查配置"
            else:
                friendly_error = f"服务暂时不可用: {error_msg}"

            logger.warning(f"[POST /api/chat/stream] 友好错误信息: {friendly_error}")

            yield {
                "event": "error",
                "data": json.dumps({"error": friendly_error}, ensure_ascii=False)
            }

    return EventSourceResponse(event_generator())
