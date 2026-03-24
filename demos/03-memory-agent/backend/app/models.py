"""
Pydantic 数据模型定义
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Literal
from datetime import datetime


# ========== 认证相关 ==========
class RegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, description="密码（至少6位）")


class LoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class User(BaseModel):
    """用户信息"""
    id: str = Field(..., description="用户 ID")
    username: str = Field(..., description="用户名")
    created_at: datetime = Field(..., description="创建时间")


class AuthResponse(BaseModel):
    """认证响应"""
    user: User = Field(..., description="用户信息")
    token: str = Field(..., description="JWT Token")


# ========== 聊天相关 ==========
class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., min_length=1, description="用户消息")
    session_id: Optional[str] = Field(None, description="会话 ID")


class ChatResponse(BaseModel):
    """聊天响应（非流式）"""
    response: str = Field(..., description="AI 响应")
    session_id: str = Field(..., description="会话 ID")


class ToolCall(BaseModel):
    """工具调用信息"""
    name: str = Field(..., description="工具名称")
    arguments: dict = Field(default_factory=dict, description="工具参数")


class SSEEvent(BaseModel):
    """SSE 事件"""
    type: Literal["token", "tool_call", "tool_result", "done", "error"] = Field(
        ...,
        description="事件类型"
    )
    content: Optional[str] = Field(None, description="内容（token/tool_result）")
    tool: Optional[str] = Field(None, description="工具名称（tool_call）")
    args: Optional[dict] = Field(None, description="工具参数（tool_call）")
    session_id: Optional[str] = Field(None, description="会话 ID（done）")
    error: Optional[str] = Field(None, description="错误信息（error）")


class Message(BaseModel):
    """对话消息"""
    id: str = Field(..., description="消息 ID")
    role: Literal["user", "assistant", "system"] = Field(..., description="角色")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(..., description="时间戳")
    tool_calls: Optional[List[ToolCall]] = Field(None, description="工具调用列表")


class Session(BaseModel):
    """会话"""
    id: str = Field(..., description="会话 ID")
    user_id: str = Field(..., description="用户 ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    messages: List[Message] = Field(default_factory=list, description="消息列表")
