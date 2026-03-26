"""
MemoryManager - 记忆管理核心类
负责摘要触发判断、摘要生成、上下文构建
"""
from typing import List, Optional, Dict, Any

from app.db.repositories import MessageRepository, MemorySummaryRepository
from app.providers.base import ChatMessage


class MemoryManager:
    """记忆管理器

    职责：
    1. should_summarize(session_id) - 检查是否需要生成摘要
    2. generate_summary(messages) - 调用LLM生成摘要
    3. get_context(session_id) - 获取发送给LLM的上下文
    """

    # 触发阈值：每5条消息生成/更新摘要
    SUMMARY_THRESHOLD = 5
    # 有摘要时短记忆长度：最近3条消息
    SHORT_MEMORY_WITH_SUMMARY = 3
    # 无摘要时短记忆长度：最近5条消息
    SHORT_MEMORY_WITHOUT_SUMMARY = 5

    def __init__(
        self,
        message_repo: MessageRepository,
        summary_repo: MemorySummaryRepository,
        llm_client: Any,
        model: str = "glm-5"
    ):
        self.message_repo = message_repo
        self.summary_repo = summary_repo
        self.llm_client = llm_client
        self.model = model

    async def should_summarize(self, session_id: str) -> bool:
        """检查是否需要生成或更新摘要

        触发条件：
        - 首次：消息数 >= 5
        - 更新：消息数 >= 当前摘要.message_count + 5

        Args:
            session_id: 会话ID

        Returns:
            bool: 是否需要生成/更新摘要
        """
        # 获取当前会话的所有消息
        messages = await self.message_repo.find_by_session_id(session_id)
        message_count = len(messages)

        # 获取现有摘要
        existing_summary = await self.summary_repo.find_by_session_id(session_id)

        if existing_summary is None:
            # 首次生成：消息数 >= 5
            return message_count >= self.SUMMARY_THRESHOLD
        else:
            # 更新：消息数 >= 当前摘要.message_count + 5
            return message_count >= existing_summary.message_count + self.SUMMARY_THRESHOLD

    async def generate_summary(self, messages: List[Dict[str, str]]) -> str:
        """调用LLM生成摘要

        Args:
            messages: 消息列表，每条消息包含 role 和 content

        Returns:
            str: 生成的摘要内容，错误时返回空字符串
        """
        # 构建摘要生成的 prompt
        prompt = self._build_summary_prompt(messages)

        try:
            # 转换为 ChatMessage 格式
            chat_messages = [
                ChatMessage(role="system", content="你是一个对话摘要助手。请简洁总结对话的关键信息。"),
                ChatMessage(role="user", content=prompt)
            ]

            response = await self.llm_client.chat(
                model=self.model,
                messages=chat_messages
            )
            return response.content.strip() if response.content else ""
        except Exception as e:
            # 错误处理：记录错误并返回空字符串
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[MemoryManager] 摘要生成失败: {e}")
            return ""

    def _build_summary_prompt(self, messages: List[Dict[str, str]]) -> str:
        """构建摘要生成的 prompt

        Args:
            messages: 消息列表

        Returns:
            str: prompt 文本
        """
        # 格式化消息
        formatted_messages = []
        for msg in messages:
            role = "用户" if msg.get("role") == "user" else "助手"
            formatted_messages.append(f"{role}: {msg.get('content', '')}")

        conversation = "\n".join(formatted_messages)

        prompt = f"""请对以下对话进行简洁总结，提取关键信息：

对话记录：
{conversation}

总结要求：
1. 保留用户的主要意图和需求
2. 保留AI提供的关键建议和结论
3. 控制在100字以内
4. 使用第三人称客观描述

摘要："""

        return prompt

    async def get_context(self, session_id: str) -> List[Dict[str, str]]:
        """获取发送给LLM的上下文

        策略：
        - 如果有摘要：返回 [摘要系统消息] + [最近3条原始消息]
        - 无摘要：返回 [最近5条原始消息]

        Args:
            session_id: 会话ID

        Returns:
            List[Dict]: 上下文消息列表
        """
        # 获取会话消息
        messages = await self.message_repo.find_by_session_id(session_id)

        # 获取摘要
        summary = await self.summary_repo.find_by_session_id(session_id)

        if summary:
            # 有摘要：摘要 + 最近3条消息
            context = []

            # 添加摘要作为系统消息
            context.append({
                "role": "system",
                "content": f"【历史对话摘要】{summary.content}"
            })

            # 添加最近3条原始消息
            recent_messages = messages[-self.SHORT_MEMORY_WITH_SUMMARY:]
            for msg in recent_messages:
                context.append({
                    "role": msg.role,
                    "content": msg.content
                })

            return context
        else:
            # 无摘要：最近5条消息
            recent_messages = messages[-self.SHORT_MEMORY_WITHOUT_SUMMARY:]
            return [
                {
                    "role": msg.role,
                    "content": msg.content
                }
                for msg in recent_messages
            ]
