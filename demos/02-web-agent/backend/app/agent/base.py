"""
Agent 基类
负责管理对话、调用 LLM 和执行工具
"""
import logging
from typing import List, Dict, Any, AsyncIterator, Optional
from pydantic import BaseModel

from app.providers.base import LLMClient, ChatMessage, ChatResponse, ToolCall
from app.agent.tools import Tool, find_tool

# 创建日志记录器
logger = logging.getLogger(__name__)


class AgentResponse(BaseModel):
    """Agent 响应"""
    content: str
    tool_calls_executed: List[str] = []
    usage: Optional[Dict[str, int]] = None


class Agent:
    """Agent 类"""

    def __init__(
        self,
        provider: str = "zhipuai",
        api_key: str = "",
        model: str = "glm-5",
        max_iterations: int = 5
    ):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.max_iterations = max_iterations

        logger.info(f"[Agent 初始化] provider={provider}, model={model}, max_iterations={max_iterations}")

        # 消息历史
        self.messages: List[ChatMessage] = [
            ChatMessage(role="system", content=self._get_system_prompt())
        ]

        # 延迟创建客户端
        self._client: Optional[LLMClient] = None

    @property
    def client(self) -> LLMClient:
        """获取或创建 LLM 客户端"""
        if self._client is None:
            logger.debug(f"[创建 LLM 客户端] provider={self.provider}")
            self._client = create_llm_client(self.provider, self.api_key)
        return self._client

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个智能 AI 助手，可以帮助用户回答问题并使用工具完成任务。

工具调用结果会自动添加到对话中，请根据结果给用户一个友好的回复。

请用中文回复用户。"""

    def _get_tool_definitions(self) -> List[Dict[str, Any]]:
        """获取工具定义（Function Calling 格式）"""
        from app.agent.tools import tools
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            }
            for tool in tools
        ]

    async def process_message(self, message: str) -> AgentResponse:
        """处理用户消息（非流式）"""
        logger.info(f"[开始处理消息] 用户输入: {message[:100]}{'...' if len(message) > 100 else ''}")

        # 添加用户消息
        self.messages.append(ChatMessage(role="user", content=message))

        iteration = 0
        tool_calls_executed: List[str] = []
        final_usage: Optional[Dict[str, int]] = None

        while iteration < self.max_iterations:
            iteration += 1
            logger.debug(f"[迭代 {iteration}/{self.max_iterations}] 开始 LLM 调用")

            # 调用 LLM
            response = await self.client.chat(
                model=self.model,
                messages=self.messages,
                tools=self._get_tool_definitions(),
                stream=False
            )

            # 记录 LLM 响应
            logger.debug(f"[迭代 {iteration}] LLM 响应: content={response.content[:50] if response.content else 'None'}{'...' if response.content and len(response.content) > 50 else ''}, tool_calls={len(response.tool_calls) if response.tool_calls else 0} 个")

            # 保存使用情况
            if response.usage:
                final_usage = response.usage
                logger.debug(f"[Token 使用] prompt_tokens={response.usage.get('prompt_tokens', 'N/A')}, completion_tokens={response.usage.get('completion_tokens', 'N/A')}, total_tokens={response.usage.get('total_tokens', 'N/A')}")

            # 检查是否有工具调用
            if response.tool_calls:
                logger.info(f"[工具调用检测] 检测到 {len(response.tool_calls)} 个工具调用")

                # 添加助手消息（包含工具调用）
                self.messages.append(ChatMessage(
                    role="assistant",
                    content=response.content or ""
                ))

                # 执行工具调用
                for tool_call in response.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = tool_call.function.arguments

                    logger.info(f"[执行工具] name={tool_name}, args={tool_args}")

                    # 执行工具
                    tool = find_tool(tool_name)
                    if tool:
                        result = tool.execute(tool_args)
                        tool_calls_executed.append(tool_name)

                        logger.info(f"[工具结果] name={tool_name}, result={result}")

                        # 添加工具结果消息
                        self.messages.append(ChatMessage(
                            role="user",
                            content=f"[工具 {tool_name} 的结果: {result}]"
                        ))
                    else:
                        logger.warning(f"[工具未找到] name={tool_name}")

                # 继续循环
                logger.debug(f"[迭代 {iteration}] 工具调用完成，继续下一轮 LLM 调用")
                continue

            # 没有工具调用，添加最终回复
            self.messages.append(ChatMessage(
                role="assistant",
                content=response.content
            ))

            logger.info(f"[处理完成] 返回最终响应，已执行工具: {tool_calls_executed if tool_calls_executed else '无'}")
            return AgentResponse(
                content=response.content,
                tool_calls_executed=tool_calls_executed,
                usage=final_usage
            )

        # 达到最大迭代次数
        logger.warning(f"[达到最大迭代次数] max_iterations={self.max_iterations}, 已执行工具: {tool_calls_executed}")
        return AgentResponse(
            content="达到最大迭代次数",
            tool_calls_executed=tool_calls_executed,
            usage=final_usage
        )

    async def process_message_stream(self, message: str) -> AsyncIterator[str]:
        """处理用户消息（流式输出）"""
        logger.info(f"[流式处理开始] 用户输入: {message[:100]}{'...' if len(message) > 100 else ''}")

        # 添加用户消息
        self.messages.append(ChatMessage(role="user", content=message))

        # 简单的流式实现（不支持工具调用)
        token_count = 0
        async for token in self.client.chat_stream(
            model=self.model,
            messages=self.messages,
            tools=None
        ):
            token_count += 1
            yield token

        logger.info(f"[流式处理完成] 共输出 {token_count} 个 token")

        # 注意：流式模式下，消息历史需要在流结束后更新
        # 这里简化处理，假设流式内容已经完整
        # 实际实现可能需要收集所有 token 然后添加到历史

    def get_messages(self) -> List[ChatMessage]:
        """获取消息历史"""
        return self.messages.copy()

    def reset_history(self):
        """重置消息历史"""
        logger.info("[重置消息历史] 清空对话上下文")
        self.messages = [
            ChatMessage(role="system", content=self._get_system_prompt())
        ]


def create_llm_client(provider: str, api_key: str) -> LLMClient:
    """创建 LLM 客户端"""
    if provider == "zhipuai":
        from app.providers.zhipuai import ZhipuClient
        return ZhipuClient(api_key)
    else:
        raise ValueError(f"不支持的提供商: {provider}")
