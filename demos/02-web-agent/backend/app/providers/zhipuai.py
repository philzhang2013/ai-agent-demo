"""
智谱 AI 客户端适配器
支持 Function Calling API 和流式输出
"""
import json
import httpx
from typing import List, Dict, Any, AsyncIterator

from app.providers.base import LLMClient, ChatMessage, ChatResponse, ToolCall


class ZhipuClient(LLMClient):
    """智谱 AI 客户端"""

    def __init__(self, api_key: str, base_url: str = "https://open.bigmodel.cn/api/coding/paas/v4"):
        self.api_key = api_key
        self.base_url = base_url

    async def chat(
        self,
        model: str,
        messages: List[ChatMessage],
        tools: List[Dict[str, Any]] | None = None,
        stream: bool = False
    ) -> ChatResponse:
        """发送聊天请求"""
        url = f"{self.base_url}/chat/completions"

        # 转换消息格式
        request_messages = [self._convert_message(m) for m in messages]

        # 构建请求体
        request_body = {
            "model": model,
            "messages": request_messages,
            "stream": False
        }

        if tools:
            request_body["tools"] = tools

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json=request_body,
                timeout=60.0
            )

            if response.status_code != 200:
                raise Exception(f"API 错误: {response.status_code} - {response.text}")

            data = response.json()

            if "error" in data:
                raise Exception(f"智谱 AI 错误: {data['error']}")

            # 提取响应
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})

            # 处理 content（GLM-5 使用 reasoning_content，GLM-4 使用 content）
            content = message.get("reasoning_content") or message.get("content") or ""
            tool_calls = []

            # 提取工具调用
            if "tool_calls" in message and message["tool_calls"]:
                for tc in message["tool_calls"]:
                    func_args = tc["function"]["arguments"]
                    if isinstance(func_args, str):
                        func_args = json.loads(func_args)

                    tool_calls.append(ToolCall(
                        id=tc["id"],
                        type="function",
                        function={
                            "name": tc["function"]["name"],
                            "arguments": func_args
                        }
                    ))

            # 提取使用情况
            usage = None
            if "usage" in data:
                usage = {
                    "prompt_tokens": data["usage"]["prompt_tokens"],
                    "completion_tokens": data["usage"]["completion_tokens"],
                    "total_tokens": data["usage"]["total_tokens"]
                }

            return ChatResponse(
                content=content,
                tool_calls=tool_calls,
                usage=usage
            )

    async def chat_stream(
        self,
        model: str,
        messages: List[ChatMessage],
        tools: List[Dict[str, Any]] | None = None
    ) -> AsyncIterator[str]:
        """发送流式聊天请求"""
        url = f"{self.base_url}/chat/completions"

        # 转换消息格式
        request_messages = [self._convert_message(m) for m in messages]

        # 构建请求体
        request_body = {
            "model": model,
            "messages": request_messages,
            "stream": True
        }

        if tools:
            request_body["tools"] = tools

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json=request_body,
                timeout=60.0
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    error_text = error_text.decode('utf-8', errors='ignore')
                    raise Exception(f"API 错误: {response.status_code} - {error_text}")

                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue

                    data_str = line[6:]  # 移除 "data: " 前缀

                    if data_str == "[DONE]":
                        break

                    try:
                        data = json.loads(data_str)
                        choices = data.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})

                            # GLM-5 使用 reasoning_content 字段
                            # GLM-4 使用 content 字段
                            content = delta.get("reasoning_content") or delta.get("content", "")
                            if content:
                                yield content
                    except (json.JSONDecodeError, KeyError):
                        continue

    def _convert_message(self, message: ChatMessage) -> Dict[str, Any]:
        """转换消息格式"""
        return {
            "role": message.role,
            "content": message.content
        }
