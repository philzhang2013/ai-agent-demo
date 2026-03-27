"""
Agent 基类
负责管理对话、调用 LLM 和执行工具
"""
import json
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

你有以下工具可以使用：
1. calculator - 执行数学计算（如：计算 1+1）
2. get_weather - 查询城市天气（如：查询北京的天气）

当用户的问题涉及到数学计算或天气查询时，你必须使用相应的工具来获取准确信息。

**重要**：对于需要计算或天气查询的问题，请直接调用工具，不要自己编造答案。

工具调用结果会自动添加到对话中，请根据工具返回的结果给用户一个友好的回复。

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

    async def process_message_stream(self, message: str) -> AsyncIterator[Dict[str, Any]]:
        """
        处理用户消息（流式输出，支持工具调用）

        返回事件字典:
        - {"event": "reasoning", "content": "..."} - 思维链内容
        - {"event": "content", "content": "..."} - 普通内容
        - {"event": "tool_call", "tool_calls": [...]} - 工具调用
        - {"event": "tool_result", "tool": "...", "result": "..."} - 工具结果
        - {"event": "tool_error", "tool": "...", "error": "..."} - 工具错误
        """
        logger.info(f"[流式处理开始] 用户输入: {message[:100]}{'...' if len(message) > 100 else ''}")

        # 添加用户消息
        self.messages.append(ChatMessage(role="user", content=message))

        # 转换消息为可读格式用于日志
        messages_for_log = [{"role": m.role, "content": m.content} for m in self.messages]
        logger.info(f"[流式处理] 消息历史: {json.dumps(messages_for_log, ensure_ascii=False)}")

        iteration = 0
        tool_calls_executed: List[str] = []

        while iteration < self.max_iterations:
            iteration += 1
            logger.debug(f"[流式迭代 {iteration}/{self.max_iterations}] 开始 LLM 调用")

            # 获取工具定义
            tool_definitions = self._get_tool_definitions()
            logger.info(f"[流式迭代 {iteration}] 工具定义: {json.dumps(tool_definitions, ensure_ascii=False, indent=2)}")

            # 调用 LLM 流式接口
            event_count = 0
            reasoning_buffer = []
            content_buffer = []
            tool_calls_buffer = []

            try:
                async for event in self.client.chat_stream(
                    model=self.model,
                    messages=self.messages,
                    tools=tool_definitions
                ):
                    event_count += 1

                    # 处理不同类型的事件
                    if event["event"] == "reasoning":
                        reasoning_buffer.append(event["content"])
                        yield event
                    elif event["event"] == "content":
                        content_buffer.append(event["content"])
                        yield event
                    elif event["event"] == "tool_call":
                        # 检测到工具调用
                        tool_calls_data = event["tool_calls"]
                        logger.info(f"[流式工具调用检测] 检测到 {len(tool_calls_data)} 个工具调用: {json.dumps(tool_calls_data, ensure_ascii=False)}")
                        tool_calls_buffer.extend(tool_calls_data)
                        yield event

                logger.info(f"[流式迭代 {iteration}] LLM 响应完成, events={event_count}")

                # 如果有工具调用，执行并继续
                if tool_calls_buffer:
                    logger.info(f"[流式工具执行] 开始执行 {len(tool_calls_buffer)} 个工具")

                    # 添加助手消息（包含工具调用）到历史
                    full_content = ""
                    if reasoning_buffer:
                        full_content += "".join(reasoning_buffer)
                    if content_buffer:
                        full_content += "".join(content_buffer)

                    self.messages.append(ChatMessage(
                        role="assistant",
                        content=full_content
                    ))

                    # 执行每个工具调用
                    for tool_call_data in tool_calls_buffer:
                        tool_name = tool_call_data["function"]["name"]
                        tool_args_str = tool_call_data["function"]["arguments"]

                        # 解析参数
                        try:
                            if isinstance(tool_args_str, str):
                                tool_args = json.loads(tool_args_str)
                            else:
                                tool_args = tool_args_str
                        except json.JSONDecodeError:
                            logger.error(f"[工具参数解析失败] {tool_args_str}")
                            yield {
                                "event": "tool_error",
                                "tool": tool_name,
                                "error": f"无效的参数格式: {tool_args_str}"
                            }
                            continue

                        logger.info(f"[执行工具] name={tool_name}, args={tool_args}")

                        # 执行工具
                        try:
                            tool = find_tool(tool_name)
                            if tool:
                                result = tool.execute(tool_args)
                                tool_calls_executed.append(tool_name)

                                logger.info(f"[工具结果] name={tool_name}, result={result}")

                                # 发送工具结果事件
                                yield {
                                    "event": "tool_result",
                                    "tool": tool_name,
                                    "result": result
                                }

                                # 添加工具结果消息到历史
                                self.messages.append(ChatMessage(
                                    role="user",
                                    content=f"[工具 {tool_name} 的结果: {result}]"
                                ))
                            else:
                                logger.warning(f"[工具未找到] name={tool_name}")
                                yield {
                                    "event": "tool_error",
                                    "tool": tool_name,
                                    "error": f"未找到工具: {tool_name}"
                                }
                        except Exception as e:
                            logger.error(f"[工具执行错误] name={tool_name}, error={str(e)}")
                            yield {
                                "event": "tool_error",
                                "tool": tool_name,
                                "error": str(e)
                            }

                    # 继续下一轮迭代
                    logger.debug(f"[流式迭代 {iteration}] 工具调用完成，继续下一轮")
                    continue
                else:
                    # 没有工具调用，添加最终回复到历史
                    full_content = ""
                    if reasoning_buffer:
                        full_content += "".join(reasoning_buffer)
                    if content_buffer:
                        full_content += "".join(content_buffer)

                    self.messages.append(ChatMessage(
                        role="assistant",
                        content=full_content
                    ))

                    logger.info(f"[流式处理完成] 返回最终响应，已执行工具: {tool_calls_executed if tool_calls_executed else '无'}")
                    break

            except Exception as e:
                logger.error(f"[流式处理错误] {str(e)}", exc_info=True)
                yield {
                    "event": "error",
                    "error": str(e)
                }
                break

        # 达到最大迭代次数
        if iteration >= self.max_iterations:
            logger.warning(f"[达到最大迭代次数] max_iterations={self.max_iterations}")
            yield {
                "event": "error",
                "error": "达到最大迭代次数"
            }

    async def process_message_stream_with_context(self, messages: List[Dict[str, str]]) -> AsyncIterator[Dict[str, Any]]:
        """
        使用预构建的上下文进行流式处理（用于记忆系统集成）

        Args:
            messages: 上下文消息列表，包含 system/user/assistant 角色

        返回事件字典:
        - {"event": "reasoning", "content": "..."} - 思维链内容
        - {"event": "content", "content": "..."} - 普通内容
        - {"event": "tool_call", "tool_calls": [...]} - 工具调用
        - {"event": "tool_result", "tool": "...", "result": "..."} - 工具结果
        - {"event": "tool_error", "tool": "...", "error": "..."} - 工具错误
        """
        logger.info(f"[带上下文的流式处理开始] 消息数={len(messages)}")

        # 重置消息历史，使用提供的上下文
        self.messages = [ChatMessage(role="system", content=self._get_system_prompt())]

        # 添加上下文消息（跳过第一个 system，因为我们已经添加了）
        for msg in messages:
            if msg.get("role") == "system":
                # 合并到系统提示词中
                self.messages[0] = ChatMessage(
                    role="system",
                    content=self._get_system_prompt() + "\n\n" + msg.get("content", "")
                )
            else:
                self.messages.append(ChatMessage(
                    role=msg.get("role", "user"),
                    content=msg.get("content", "")
                ))

        # 转换消息为可读格式用于日志
        messages_for_log = [{"role": m.role, "content": m.content[:50]} for m in self.messages]
        logger.info(f"[带上下文的流式处理] 消息历史: {json.dumps(messages_for_log, ensure_ascii=False)}")

        iteration = 0
        tool_calls_executed: List[str] = []

        while iteration < self.max_iterations:
            iteration += 1
            logger.debug(f"[上下文流式迭代 {iteration}/{self.max_iterations}] 开始 LLM 调用")

            # 获取工具定义
            tool_definitions = self._get_tool_definitions()

            # 调用 LLM 流式接口
            event_count = 0
            reasoning_buffer = []
            content_buffer = []
            tool_calls_buffer = []

            try:
                async for event in self.client.chat_stream(
                    model=self.model,
                    messages=self.messages,
                    tools=tool_definitions
                ):
                    event_count += 1

                    # 处理不同类型的事件
                    if event["event"] == "reasoning":
                        reasoning_buffer.append(event["content"])
                        yield event
                    elif event["event"] == "content":
                        content_buffer.append(event["content"])
                        yield event
                    elif event["event"] == "tool_calls":
                        tool_calls_buffer.extend(event["tool_calls"])
                        yield event

                logger.debug(f"[上下文流式迭代 {iteration}] 收到 {event_count} 个事件")

                # 处理工具调用
                if tool_calls_buffer:
                    yield {
                        "event": "tool_call",
                        "tool_calls": tool_calls_buffer
                    }

                    # 添加工具调用消息
                    for tc in tool_calls_buffer:
                        self.messages.append(ChatMessage(
                            role="assistant",
                            content=f"调用工具: {tc.get('name', 'unknown')}"
                        ))

                        tool_name = tc.get("name", "unknown")
                        tool_args_str = tc.get("arguments", "{}")

                        # 解析工具参数
                        try:
                            if isinstance(tool_args_str, str):
                                tool_args = json.loads(tool_args_str)
                            else:
                                tool_args = tool_args_str
                        except json.JSONDecodeError:
                            yield {
                                "event": "tool_error",
                                "tool": tool_name,
                                "error": f"无效的参数格式: {tool_args_str}"
                            }
                            continue

                        logger.info(f"[上下文执行工具] name={tool_name}, args={tool_args}")

                        # 执行工具
                        try:
                            tool = find_tool(tool_name)
                            if tool:
                                result = tool.execute(tool_args)
                                tool_calls_executed.append(tool_name)

                                yield {
                                    "event": "tool_result",
                                    "tool": tool_name,
                                    "result": result
                                }

                                self.messages.append(ChatMessage(
                                    role="user",
                                    content=f"[工具 {tool_name} 的结果: {result}]"
                                ))
                            else:
                                yield {
                                    "event": "tool_error",
                                    "tool": tool_name,
                                    "error": f"未找到工具: {tool_name}"
                                }
                        except Exception as e:
                            yield {
                                "event": "tool_error",
                                "tool": tool_name,
                                "error": str(e)
                            }

                    continue
                else:
                    # 没有工具调用，处理完成
                    full_content = ""
                    if reasoning_buffer:
                        full_content += "".join(reasoning_buffer)
                    if content_buffer:
                        full_content += "".join(content_buffer)

                    self.messages.append(ChatMessage(
                        role="assistant",
                        content=full_content
                    ))

                    logger.info(f"[上下文流式处理完成] 已执行工具: {tool_calls_executed if tool_calls_executed else '无'}")
                    break

            except Exception as e:
                logger.error(f"[上下文流式处理错误] {str(e)}", exc_info=True)
                yield {
                    "event": "error",
                    "error": str(e)
                }
                break

        # 达到最大迭代次数
        if iteration >= self.max_iterations:
            logger.warning(f"[上下文达到最大迭代次数] max_iterations={self.max_iterations}")
            yield {
                "event": "error",
                "error": "达到最大迭代次数"
            }

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
    if provider == "kimi":
        from app.providers.kimi import KimiClient
        return KimiClient(api_key)
    elif provider == "zhipuai":
        from app.providers.zhipuai import ZhipuClient
        return ZhipuClient(api_key)
    else:
        raise ValueError(f"不支持的提供商: {provider}")
