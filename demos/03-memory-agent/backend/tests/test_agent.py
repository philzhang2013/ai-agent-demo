"""
Agent 核心模块测试
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from app.agent.base import Agent
from app.agent.tools import find_tool
from app.providers.base import ChatResponse, ToolCall


class TestAgent:
    """测试 Agent 类"""

    @pytest.mark.asyncio
    async def test_should_initialize_with_provider(self):
        """测试应该使用提供商初始化"""
        mock_client = Mock()
        mock_client.chat = AsyncMock(return_value=ChatResponse(
            content="你好！",
            tool_calls=[],
            usage={"total_tokens": 10}
        ))

        with patch("app.agent.base.create_llm_client", return_value=mock_client):
            agent = Agent(provider="zhipuai", api_key="test-key")

        assert agent.provider == "zhipuai"
        assert agent.api_key == "test-key"
        assert agent.model == "glm-5"

    @pytest.mark.asyncio
    async def test_should_process_simple_message(self):
        """测试应该处理简单消息"""
        mock_client = Mock()
        mock_client.chat = AsyncMock(return_value=ChatResponse(
            content="你好！有什么我可以帮助你的吗？",
            tool_calls=[],
            usage={"total_tokens": 15}
        ))

        with patch("app.agent.base.create_llm_client", return_value=mock_client):
            agent = Agent(provider="zhipuai", api_key="test-key")
            response = await agent.process_message("你好")

        assert "你好" in response.content
        assert response.usage is not None
        assert response.usage["total_tokens"] == 15

    @pytest.mark.asyncio
    async def test_should_handle_tool_call(self):
        """测试应该处理工具调用"""
        mock_client = Mock()

        # 第一次调用返回工具调用
        mock_client.chat = AsyncMock(
            side_effect=[
                ChatResponse(
                    content="",
                    tool_calls=[
                        ToolCall(
                            id="call_123",
                            type="function",
                            function={
                                "name": "calculator",
                                "arguments": {"expression": "18+25"}
                            }
                        )
                    ],
                    usage={"total_tokens": 20}
                ),
                # 第二次调用返回最终回复
                ChatResponse(
                    content="计算结果是 43",
                    tool_calls=[],
                    usage={"total_tokens": 30}
                )
            ]
        )

        with patch("app.agent.base.create_llm_client", return_value=mock_client):
            agent = Agent(provider="zhipuai", api_key="test-key")
            response = await agent.process_message("计算 18+25")

        assert "43" in response.content
        assert response.tool_calls_executed == ["calculator"]

    @pytest.mark.asyncio
    async def test_should_stream_response(self):
        """测试应该流式输出响应"""
        async def mock_stream(*args, **kwargs):
            yield {"event": "content", "content": "你"}
            yield {"event": "content", "content": "好"}
            yield {"event": "content", "content": "！"}

        mock_client = Mock()
        mock_client.chat_stream = mock_stream

        with patch("app.agent.base.create_llm_client", return_value=mock_client):
            agent = Agent(provider="zhipuai", api_key="test-key")
            tokens = []
            async for token in agent.process_message_stream("你好"):
                tokens.append(token)

        # 现在返回的是事件字典，不是字符串
        assert len(tokens) == 3
        assert tokens[0] == {"event": "content", "content": "你"}
        assert tokens[1] == {"event": "content", "content": "好"}
        assert tokens[2] == {"event": "content", "content": "！"}

    @pytest.mark.asyncio
    async def test_should_track_message_history(self):
        """测试应该跟踪消息历史"""
        mock_client = Mock()
        mock_client.chat = AsyncMock(return_value=ChatResponse(
            content="收到",
            tool_calls=[],
            usage={"total_tokens": 10}
        ))

        with patch("app.agent.base.create_llm_client", return_value=mock_client):
            agent = Agent(provider="zhipuai", api_key="test-key")
            await agent.process_message("第一条消息")
            await agent.process_message("第二条消息")

        assert len(agent.get_messages()) == 5  # system + user + assistant + user + assistant

    @pytest.mark.asyncio
    async def test_should_reset_history(self):
        """测试应该重置历史"""
        mock_client = Mock()
        mock_client.chat = AsyncMock(return_value=ChatResponse(
            content="收到",
            tool_calls=[],
            usage={"total_tokens": 10}
        ))

        with patch("app.agent.base.create_llm_client", return_value=mock_client):
            agent = Agent(provider="zhipuai", api_key="test-key")
            await agent.process_message("消息")
            agent.reset_history()

        assert len(agent.get_messages()) == 1  # 只有 system 消息


class TestAgentResponse:
    """测试 Agent 响应模型"""

    def test_should_create_response(self):
        """测试应该创建响应"""
        from app.agent.base import AgentResponse

        response = AgentResponse(
            content="你好",
            tool_calls_executed=["calculator"],
            usage={"total_tokens": 20}
        )

        assert response.content == "你好"
        assert response.tool_calls_executed == ["calculator"]
        assert response.usage["total_tokens"] == 20
