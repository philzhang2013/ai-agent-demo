"""
Kimi AI 客户端适配器
与 OpenAI API 格式兼容
"""
import json
import logging
import httpx
from typing import List, Dict, Any, AsyncIterator

from app.providers.base import LLMClient, ChatMessage, ChatResponse, ToolCall

logger = logging.getLogger(__name__)


class KimiClient(LLMClient):
    """Kimi AI 客户端"""

    def __init__(self, api_key: str, base_url: str = "https://api.moonshot.cn/v1"):
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

        logger.info(f"[Kimi chat] request_messages: {request_messages}")

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
                error_text = response.text
                # 处理特定错误码
                if response.status_code == 429:
                    raise Exception("Kimi 服务繁忙，请稍后重试 (429)")
                elif response.status_code == 401:
                    raise Exception("Kimi API 认证失败，请检查 API Key (401)")
                elif response.status_code == 403:
                    raise Exception("Kimi API 权限不足 (403)")
                else:
                    raise Exception(f"Kimi API 错误: {response.status_code} - {error_text}")

            data = response.json()

            if "error" in data:
                error_msg = data["error"].get("message", "Unknown error")
                raise Exception(f"Kimi AI 错误: {error_msg}")

            # 提取响应
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})

            # content 可能为 None，默认为空字符串
            content = message.get("content") or ""
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
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        发送流式聊天请求

        返回事件字典:
        - {"event": "content", "content": "..."} - 普通内容
        - {"event": "tool_call", "tool_calls": [...]} - 工具调用
        """
        url = f"{self.base_url}/chat/completions"

        # 转换消息格式
        request_messages = [self._convert_message(m) for m in messages]
        logger.info(f"[Kimi chat] request_messages: {json.dumps(request_messages, ensure_ascii=False)}")

        # 构建请求体
        request_body = {
            "model": model,
            "messages": request_messages,
            "stream": True
        }

        if tools:
            request_body["tools"] = tools

        logger.info(f"[Kimi chat_stream] request_body: {json.dumps(request_body, ensure_ascii=False, indent=2)}")

        # 用于累积 tool_calls 数据
        current_tool_calls: List[Dict[str, Any]] = []

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
                    # 处理特定错误码
                    if response.status_code == 429:
                        raise Exception("Kimi 服务繁忙，请稍后重试 (429)")
                    elif response.status_code == 401:
                        raise Exception("Kimi API 认证失败，请检查 API Key (401)")
                    elif response.status_code == 403:
                        raise Exception("Kimi API 权限不足 (403)")
                    else:
                        raise Exception(f"Kimi API 错误: {response.status_code} - {error_text}")

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
                            finish_reason = choices[0].get("finish_reason", "")

                            # 检测 tool_calls（流式模式）
                            if "tool_calls" in delta and delta["tool_calls"]:
                                # 累积 tool_calls 数据
                                for tc in delta["tool_calls"]:
                                    index = tc.get("index", 0)
                                    # 确保数组有足够空间
                                    while len(current_tool_calls) <= index:
                                        current_tool_calls.append({
                                            "id": "",
                                            "type": "function",
                                            "function": {"name": "", "arguments": ""}
                                        })

                                    # 更新 tool_call 数据
                                    if "id" in tc:
                                        current_tool_calls[index]["id"] = tc["id"]
                                    if "function" in tc:
                                        func = tc["function"]
                                        if "name" in func:
                                            current_tool_calls[index]["function"]["name"] = func["name"]
                                        if "arguments" in func:
                                            # arguments 是逐步追加的
                                            current_tool_calls[index]["function"]["arguments"] += func["arguments"]

                            # 检测是否完成（finish_reason = tool_calls）
                            if finish_reason == "tool_calls" and current_tool_calls:
                                logger.info(f"[流式工具调用检测] tool_calls: {current_tool_calls}")
                                yield {
                                    "event": "tool_call",
                                    "tool_calls": current_tool_calls
                                }
                                current_tool_calls = []

                            # 处理普通内容
                            content = delta.get("content", "")
                            if content:
                                yield {
                                    "event": "content",
                                    "content": content
                                }
                    except (json.JSONDecodeError, KeyError):
                        continue

    def _convert_message(self, message: ChatMessage) -> Dict[str, Any]:
        """转换消息格式"""
        return {
            "role": message.role,
            "content": message.content
        }
