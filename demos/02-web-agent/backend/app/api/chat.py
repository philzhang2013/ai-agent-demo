"""
聊天端点
支持 SSE 流式输出
"""
import json
import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from app.models import ChatRequest, ChatResponse
from app.agent.base import Agent
from app.config import get_settings

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)


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
    try:
        response = await agent.process_message(request.message)
        return ChatResponse(
            response=response.content,
            session_id=request.session_id or "default-session"
        )
    except Exception as e:
        logger.error(f"聊天错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(request: ChatRequest, agent: Agent = Depends(get_agent)):
    """流式聊天端点（SSE）"""

    async def event_generator():
        """生成 SSE 事件"""
        try:
            # 使用 Agent 的流式处理方法
            async for token in agent.process_message_stream(request.message):
                yield {
                    "event": "token",
                    "data": json.dumps({"content": token})
                }

            # 发送完成事件
            yield {
                "event": "done",
                "data": json.dumps({"session_id": request.session_id or "default"})
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"流式聊天错误: {error_msg}")

            # 提供更友好的错误信息
            if "1113" in error_msg or "余额不足" in error_msg:
                friendly_error = "API 余额不足，请联系管理员充值"
            elif "429" in error_msg or "频率" in error_msg:
                friendly_error = "请求过于频繁，请稍后再试"
            elif "401" in error_msg or "403" in error_msg:
                friendly_error = "API 认证失败，请检查配置"
            else:
                friendly_error = f"服务暂时不可用: {error_msg}"

            # 发送错误事件
            yield {
                "event": "error",
                "data": json.dumps({"error": friendly_error})
            }

    return EventSourceResponse(event_generator())
