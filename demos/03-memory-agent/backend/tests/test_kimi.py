"""
Kimi LLM 提供商适配器测试
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from httpx import Response

from app.providers.kimi import KimiClient
from app.providers.base import ChatMessage


class TestKimiClient:
    """测试 Kimi AI 客户端"""

    def test_should_initialize_with_api_key(self):
        """测试应该使用 API Key 初始化"""
        client = KimiClient("test-api-key")
        assert client.api_key == "test-api-key"
        assert client.base_url == "https://api.moonshot.cn/v1"

    def test_should_initialize_with_custom_base_url(self):
        """测试应该使用自定义 Base URL"""
        client = KimiClient("test-api-key", "https://custom.api.com")
        assert client.api_key == "test-api-key"
        assert client.base_url == "https://custom.api.com"

    @pytest.mark.asyncio
    async def test_should_send_chat_request(self):
        """测试应该发送聊天请求"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "chat-123",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "你好！"
                }
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            }
        }

        async def mock_post(*args, **kwargs):
            return mock_response

        with patch("httpx.AsyncClient.post", mock_post):
            client = KimiClient("test-api-key")
            response = await client.chat(
                model="kimi-for-coding",
                messages=[ChatMessage(role="user", content="你好")],
                stream=False
            )

        assert response.content == "你好！"
        assert response.usage is not None
        assert response.usage["total_tokens"] == 15

    @pytest.mark.asyncio
    async def test_should_handle_tool_calls(self):
        """测试应该处理工具调用"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "chat-456",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": "call_123",
                        "type": "function",
                        "function": {
                            "name": "calculator",
                            "arguments": '{"expression": "1+1"}'
                        }
                    }]
                }
            }],
            "usage": {
                "prompt_tokens": 20,
                "completion_tokens": 10,
                "total_tokens": 30
            }
        }

        async def mock_post(*args, **kwargs):
            return mock_response

        with patch("httpx.AsyncClient.post", mock_post):
            client = KimiClient("test-api-key")
            response = await client.chat(
                model="kimi-for-coding",
                messages=[ChatMessage(role="user", content="计算1+1")],
                tools=[],
                stream=False
            )

        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].id == "call_123"
        assert response.tool_calls[0].function.name == "calculator"
        assert response.tool_calls[0].function.arguments == {"expression": "1+1"}

    @pytest.mark.asyncio
    async def test_should_handle_api_error(self):
        """测试应该处理 API 错误"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        async def mock_post(*args, **kwargs):
            return mock_response

        with patch("httpx.AsyncClient.post", mock_post):
            client = KimiClient("test-api-key")
            with pytest.raises(Exception) as exc_info:
                await client.chat(
                    model="kimi-for-coding",
                    messages=[ChatMessage(role="user", content="你好")],
                    stream=False
                )

        assert "401" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_should_handle_error_response(self):
        """测试应该处理 API 返回的错误信息"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "error": {
                "message": "模型不存在",
                "type": "invalid_request_error"
            }
        }

        async def mock_post(*args, **kwargs):
            return mock_response

        with patch("httpx.AsyncClient.post", mock_post):
            client = KimiClient("test-api-key")
            with pytest.raises(Exception) as exc_info:
                await client.chat(
                    model="invalid-model",
                    messages=[ChatMessage(role="user", content="你好")],
                    stream=False
                )

        assert "模型不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_should_send_streaming_request(self):
        """测试应该发送流式请求"""
        async def mock_aiter_lines():
            chunks = [
                'data: {"id":"chat-789","choices":[{"delta":{"content":"你"}}]}\n\n',
                'data: {"id":"chat-789","choices":[{"delta":{"content":"好"}}]}\n\n',
                'data: {"id":"chat-789","choices":[{"delta":{"content":"！"}}]}\n\n',
                'data: [DONE]\n\n'
            ]
            for chunk in chunks:
                yield chunk

        class MockAsyncContext:
            def __init__(self):
                self.client = MagicMock()
                self.client.status_code = 200

            async def __aenter__(self):
                return self.client

            async def __aexit__(self, *args):
                pass

        mock_stream_context = MockAsyncContext()
        mock_stream_context.client.aiter_lines = mock_aiter_lines

        mock_client = MagicMock()
        mock_client.stream = MagicMock(return_value=mock_stream_context)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock()

        with patch("httpx.AsyncClient", return_value=mock_client):
            client = KimiClient("test-api-key")
            tokens = []
            async for token in client.chat_stream(
                model="kimi-for-coding",
                messages=[ChatMessage(role="user", content="你好")],
            ):
                tokens.append(token)

        assert len(tokens) == 3
        assert tokens[0] == {"event": "content", "content": "你"}
        assert tokens[1] == {"event": "content", "content": "好"}
        assert tokens[2] == {"event": "content", "content": "！"}

    @pytest.mark.asyncio
    async def test_should_handle_streaming_tool_calls(self):
        """测试应该处理流式工具调用"""
        async def mock_aiter_lines():
            chunks = [
                'data: {"id":"chat-abc","choices":[{"delta":{"tool_calls":[{"index":0,"id":"call_123","type":"function","function":{"name":"calculator"}}]}}]}\n\n',
                'data: {"id":"chat-abc","choices":[{"delta":{"tool_calls":[{"index":0,"function":{"arguments":"{\\"expression\\": \"1"}}]}}]}\n\n',
                'data: {"id":"chat-abc","choices":[{"delta":{"tool_calls":[{"index":0,"function":{"arguments":"+1\"}"}}]}}]}\n\n',
                'data: {"id":"chat-abc","choices":[{"finish_reason":"tool_calls"}]}\n\n',
            ]
            for chunk in chunks:
                yield chunk

        class MockAsyncContext:
            def __init__(self):
                self.client = MagicMock()
                self.client.status_code = 200

            async def __aenter__(self):
                return self.client

            async def __aexit__(self, *args):
                pass

        mock_stream_context = MockAsyncContext()
        mock_stream_context.client.aiter_lines = mock_aiter_lines

        mock_client = MagicMock()
        mock_client.stream = MagicMock(return_value=mock_stream_context)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock()

        with patch("httpx.AsyncClient", return_value=mock_client):
            client = KimiClient("test-api-key")
            events = []
            async for event in client.chat_stream(
                model="kimi-for-coding",
                messages=[ChatMessage(role="user", content="计算1+1")],
            ):
                events.append(event)

        # 应该有一个 tool_call 事件
        tool_call_events = [e for e in events if e["event"] == "tool_call"]
        assert len(tool_call_events) == 1
        assert len(tool_call_events[0]["tool_calls"]) == 1
        assert tool_call_events[0]["tool_calls"][0]["function"]["name"] == "calculator"
