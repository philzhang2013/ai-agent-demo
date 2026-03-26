"""
智谱 AI 客户端适配器
支持 Function Calling API 和流式输出
"""
import json
import logging
import httpx
from typing import List, Dict, Any, AsyncIterator

from app.providers.base import LLMClient, ChatMessage, ChatResponse, ToolCall
logger = logging.getLogger(__name__)

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

        logger.info(f"[智普 chat] request_messages: {request_messages}")
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

            # 处理 content（GLM-5 可能同时返回 reasoning_content 和 content）
            # reasoning_content 是思维链，content 是实际回复内容
            # 对于摘要生成等场景，应该使用 content 而不是 reasoning_content
            content = message.get("content") or message.get("reasoning_content") or ""
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
        - {"event": "reasoning", "content": "..."} - 思维链内容
        - {"event": "content", "content": "..."} - 普通内容
        - {"event": "tool_call", "tool_calls": [...]} - 工具调用
        """
        url = f"{self.base_url}/chat/completions"

        # 转换消息格式
        request_messages = [self._convert_message(m) for m in messages]
        logger.info(f"[智普zhipu chat] request_messages: {json.dumps(request_messages, ensure_ascii=False)}")

        # 构建请求体
        request_body = {
            "model": model,
            "messages": request_messages,
            "stream": True
        }

        # 启用思维链功能（仅 GLM-4.5+ 和 GLM-4.1V-Thinking 支持）
        if model.startswith("glm-4.5") or "thinking" in model.lower():
            request_body["thinking"] = {"type": "enabled"}

        if tools:
            request_body["tools"] = tools

        logger.info(f"[智普zhipu chat_stream] request_body: {json.dumps(request_body, ensure_ascii=False, indent=2)}")

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

                            # 处理普通内容（reasoning_content 和 content）
                            # GLM-4.5+ 使用 reasoning_content 字段表示思维链
                            # GLM-4 使用 content 字段表示普通内容
                            reasoning_content = delta.get("reasoning_content", "")
                            content = delta.get("content", "")

                            if reasoning_content:
                                yield {
                                    "event": "reasoning",
                                    "content": reasoning_content
                                }
                            elif content:
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
