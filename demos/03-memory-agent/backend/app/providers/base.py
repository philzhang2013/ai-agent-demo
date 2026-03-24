"""
LLM 提供商基类和接口定义
"""
from typing import Optional, List, Dict, Any, AsyncIterator
from pydantic import BaseModel
from abc import ABC, abstractmethod


class FunctionCall(BaseModel):
    """函数调用"""
    name: str
    arguments: Dict[str, Any] | str


class ToolCall(BaseModel):
    """工具调用"""
    id: str
    type: str = "function"
    function: FunctionCall


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str
    content: str


class ChatResponse(BaseModel):
    """聊天响应"""
    content: str = ""
    tool_calls: List[ToolCall] = []
    usage: Optional[Dict[str, int]] = None


class LLMClient(ABC):
    """LLM 客户端基类"""

    @abstractmethod
    async def chat(
        self,
        model: str,
        messages: List[ChatMessage],
        tools: List[Dict[str, Any]] | None = None,
        stream: bool = False
    ) -> ChatResponse:
        """发送聊天请求"""
        pass

    @abstractmethod
    async def chat_stream(
        self,
        model: str,
        messages: List[ChatMessage],
        tools: List[Dict[str, Any]] | None = None
    ) -> AsyncIterator[str]:
        """发送流式聊天请求"""
        pass
