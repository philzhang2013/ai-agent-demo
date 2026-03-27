# API 文档

## RESTful API

| 方法   | 端点                       | 描述                 | 认证 |
| ------ | -------------------------- | -------------------- | ---- |
| GET    | `/api/health`              | 健康检查             | ❌   |
| POST   | `/api/auth/register`       | 用户注册             | ❌   |
| POST   | `/api/auth/login`          | 用户登录             | ❌   |
| GET    | `/api/auth/me`             | 获取当前用户         | ✅   |
| POST   | `/api/chat/stream`         | 发送消息（SSE）      | ❌   |
| POST   | `/api/chat/{id}/analyze`   | 分析会话记忆         | ❌   |
| GET    | `/api/chat/{id}/memory`    | 获取/搜索会话记忆    | ❌   |
| GET    | `/api/sessions`            | 获取会话列表         | ✅   |
| GET    | `/api/sessions/{id}`       | 获取会话详情         | ✅   |
| POST   | `/api/sessions`            | 创建新会话           | ✅   |
| DELETE | `/api/sessions/{id}`       | 删除会话             | ✅   |
| PUT    | `/api/sessions/{id}/title` | 更新会话标题         | ✅   |

## SSE 事件流

```
event: token
data: {"content": "你"}

event: token
data: {"content": "好"}

event: tool_call
data: {"tool": "calculator", "args": {"expression": "18+25"}}

event: tool_result
data: {"content": "计算结果: 43"}

event: done
data: {"session_id": "uuid"}
```

## 非流式聊天端点

| 方法 | 端点        | 描述               | 认证 |
| ---- | ----------- | ------------------ | ---- |
| POST | `/api/chat` | 发送消息（非流式） | ❌   |

详细 API 文档请访问：[http://localhost:8000/docs](http://localhost:8000/docs)

## 扩展指南

### 添加新的 LLM 提供商

1. 在 `backend/app/providers/` 创建新文件（如 `openai.py`）
2. 继承 `LLMClient` 基类，实现 `chat()` 和 `chat_stream()` 方法
3. 在 `backend/app/agent/base.py` 的 `create_llm_client()` 中添加条件分支

```python
# backend/app/providers/openai.py
from .base import LLMClient

class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def chat(self, messages: list, tools: list = None) -> dict:
        # 实现同步聊天
        pass

    def chat_stream(self, messages: list, tools: list = None):
        # 实现流式聊天
        pass
```

### 添加新工具

1. 在 `backend/app/agent/tools.py` 定义工具函数
2. 创建 `Tool` 实例并添加到 `tools` 列表
3. 工具自动注册到 Agent 的 Function Calling 定义中

```python
# backend/app/agent/tools.py
from .base import Tool

def my_new_tool(param: str) -> str:
    """工具描述"""
    return f"结果: {param}"

# 添加到 tools 列表
tools.append(Tool(
    name="my_new_tool",
    description="工具描述",
    func=my_new_tool,
    parameters={
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "参数描述"}
        },
        "required": ["param"]
    }
))
```

### 添加新的 API 端点

1. 在 `backend/app/api/` 创建新文件（如 `users.py`）
2. 定义路由和处理器函数
3. 在 `backend/app/main.py` 中注册路由

```python
# backend/app/api/users.py
from fastapi import APIRouter, Depends
from ..auth.dependencies import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/profile")
async def get_profile(current_user = Depends(get_current_user)):
    return {"username": current_user.username}
```

```python
# backend/app/main.py
from .api.users import router as users_router
app.include_router(users_router)
```
