"""
智能记忆管理器
集成 ImportanceScorer、TopicSegmenter、VectorStore
提供统一的分层记忆管理接口
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from app.memory.importance_scorer import ImportanceScorer
from app.memory.topic_segmenter import TopicSegmenter, TopicSegment
from app.memory.vector_store import VectorStore
from app.db.repositories import ImportanceScoreRepository, MemorySegmentRepository


class SmartMemoryManager:
    """
    智能记忆管理器

    职责：
    1. 处理消息流，评估重要性
    2. 按主题分段存储长记忆
    3. 生成和管理向量嵌入
    4. 提供语义检索能力
    """

    def __init__(
        self,
        importance_scorer: Optional[ImportanceScorer] = None,
        topic_segmenter: Optional[TopicSegmenter] = None,
        vector_store: Optional[VectorStore] = None,
        importance_repo: Optional[ImportanceScoreRepository] = None,
        segment_repo: Optional[MemorySegmentRepository] = None,
    ):
        self.importance_scorer = importance_scorer or ImportanceScorer()
        self.topic_segmenter = topic_segmenter or TopicSegmenter()
        self.vector_store = vector_store
        self.importance_repo = importance_repo
        self.segment_repo = segment_repo

    async def process_message(self, message: Dict[str, Any]) -> bool:
        """
        处理单条消息：评分、生成向量、存储

        Args:
            message: {id, session_id, content, created_at}

        Returns:
            是否成功处理
        """
        try:
            content = message.get("content", "")
            message_id = message.get("id")
            session_id = message.get("session_id")
            # 1. 重要性评分
            importance_score = self.importance_scorer.score(content)

            # 2. 存储重要性分数
            if self.importance_repo:
                await self.importance_repo.update_score(
                    message_id=message_id,
                    importance_score=importance_score
                )

            # 3. 生成并存储向量（如果有 VectorStore）
            if self.vector_store and self.importance_repo:
                embedding = self.vector_store.embed(content)

                if embedding:
                    await self.importance_repo.update_embedding(
                        message_id=message_id,
                        embedding=embedding
                    )

            return True
        except Exception as e:
            # 记录错误但不中断流程
            print(f"处理消息时出错: {e}")
            return False

    async def batch_score_messages(
        self,
        messages: List[Dict[str, Any]]
    ) -> List[float]:
        """
        批量评分消息

        Args:
            messages: [{content}, ...]

        Returns:
            重要性分数列表
        """
        contents = [msg.get("content", "") for msg in messages]
        return self.importance_scorer.score_batch(contents)

    async def create_topic_segments(
        self,
        session_id: str,
        messages: List[Dict[str, Any]]
    ) -> List[TopicSegment]:
        """
        创建主题段（长记忆）

        Args:
            session_id: 会话 ID
            messages: 消息列表

        Returns:
            主题段列表
        """
        if not messages:
            return []

        # 使用 TopicSegmenter 进行分段
        segments = self.topic_segmenter.segment(messages)

        # 存储到数据库（如果有 Repository）
        if self.segment_repo:
            for segment in segments:
                # 生成向量嵌入
                embedding = None
                if self.vector_store:
                    embedding = self.vector_store.embed(segment.summary)

                await self.segment_repo.create(
                    session_id=session_id,
                    topic_name=segment.topic_name,
                    start_message_id=segment.start_message_id,
                    end_message_id=segment.end_message_id,
                    summary_content=segment.summary,
                    importance_score=segment.importance_score,
                    message_count=segment.message_count,
                    total_importance=segment.importance_score * segment.message_count,
                    embedding=embedding
                )

                # 将 topic_name 回写到 messages 表的 topic_tag 字段
                if self.importance_repo:
                    await self._update_messages_topic_tag(
                        segment=segment,
                        topic_name=segment.topic_name,
                        all_messages=messages
                    )

        return segments

    async def _update_messages_topic_tag(
        self,
        segment: TopicSegment,
        topic_name: str,
        all_messages: List[Dict[str, Any]]
    ) -> None:
        """
        将主题名称更新到该段所有消息的 topic_tag 字段

        Args:
            segment: 主题段
            topic_name: 主题名称
            all_messages: 该会话的所有消息列表
        """
        logger.debug(f"更新消息 topic_tag: segment={segment.topic_name}, "
                    f"start={segment.start_message_id}, end={segment.end_message_id}")

        # 找到该段内的所有消息 ID
        segment_message_ids = []
        in_segment = False

        for msg in all_messages:
            msg_id = msg.get("id")
            if msg_id == segment.start_message_id:
                in_segment = True
            if in_segment:
                segment_message_ids.append(str(msg_id))
            if msg_id == segment.end_message_id:
                break

        if segment_message_ids and hasattr(self.importance_repo, 'batch_update_topic_tags'):
            # 批量更新该段所有消息的 topic_tag
            updated_count = await self.importance_repo.batch_update_topic_tags(
                message_ids=segment_message_ids,
                topic_tag=topic_name
            )
            logger.debug(f"已更新 {updated_count} 条消息的 topic_tag")
        elif segment_message_ids:
            # 如果没有批量更新方法，逐个更新
            for msg_id in segment_message_ids:
                score = await self.importance_repo.get_score(msg_id)
                await self.importance_repo.update_score(
                    message_id=msg_id,
                    importance_score=score,
                    topic_tag=topic_name
                )

    async def semantic_search(
        self,
        session_id: str,
        query: str,
        limit: int = 5
    ) -> List[TopicSegment]:
        """
        语义搜索主题段

        Args:
            session_id: 会话 ID
            query: 查询文本
            limit: 返回结果数量

        Returns:
            相关主题段列表
        """
        if not self.vector_store or not self.segment_repo:
            return []

        # 1. 生成查询向量
        query_embedding = self.vector_store.embed(query)
        if not query_embedding:
            return []

        # 2. 执行语义搜索
        results = await self.segment_repo.semantic_search(
            session_id=session_id,
            query_embedding=query_embedding,
            limit=limit
        )

        return results

    async def get_high_importance_messages(
        self,
        session_id: str,
        threshold: float = 0.7,
        limit: int = 20
    ) -> List[tuple]:
        """
        获取高重要性消息

        Args:
            session_id: 会话 ID
            threshold: 重要性阈值
            limit: 返回数量

        Returns:
            [(message_id, importance_score, content), ...]
        """
        if not self.importance_repo:
            return []

        return await self.importance_repo.get_messages_by_importance_threshold(
            session_id=session_id,
            min_importance=threshold,
            limit=limit
        )

    async def build_context(
        self,
        session_id: str,
        current_message: str,
        max_tokens: int = 2000
    ) -> str:
        """
        构建对话上下文（使用分层记忆）

        策略：
        1. 包含高重要性消息
        2. 包含相关主题段摘要
        3. 控制在 token 限制内

        Args:
            session_id: 会话 ID
            current_message: 当前消息
            max_tokens: 最大 token 数

        Returns:
            上下文字符串
        """
        context_parts = []

        # 1. 获取高重要性消息
        if self.importance_repo:
            high_importance = await self.get_high_importance_messages(
                session_id=session_id,
                threshold=0.75,
                limit=5
            )
            if high_importance:
                context_parts.append("## 重要信息")
                for msg_id, score, content in high_importance:
                    context_parts.append(f"- {content}")

        # 2. 获取相关主题段
        if self.segment_repo:
            segments = await self.segment_repo.find_by_session_id(session_id)
            if segments:
                context_parts.append("\n## 相关话题")
                for segment in segments[:3]:  # 取前3个主题
                    if segment.importance_score > 0.6:
                        context_parts.append(f"【{segment.topic_name}】: {segment.summary_content}")

        context = "\n".join(context_parts)

        # 简单截断控制长度（实际应该使用 tokenizer）
        if len(context) > max_tokens * 4:  # 粗略估计 1 token ≈ 4 字符
            context = context[:max_tokens * 4] + "..."

        return context if context else "无相关上下文"

    def calculate_session_importance(
        self,
        messages: List[Dict[str, Any]]
    ) -> float:
        """
        计算会话整体重要性

        Args:
            messages: 消息列表

        Returns:
            平均重要性分数
        """
        if not messages:
            return 0.0

        contents = [msg.get("content", "") for msg in messages]
        scores = self.importance_scorer.score_batch(contents)

        if not scores:
            return 0.0

        return round(sum(scores) / len(scores), 3)

    async def analyze_session(
        self,
        session_id: str,
        messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        分析会话，生成分层记忆

        Args:
            session_id: 会话 ID
            messages: 消息列表

        Returns:
            分析结果
        """
        # 1. 计算整体重要性
        avg_importance = self.calculate_session_importance(messages)

        # 2. 创建主题段
        segments = await self.create_topic_segments(session_id, messages)

        # 3. 统计信息
        topic_names = [s.topic_name for s in segments]

        return {
            "session_id": session_id,
            "message_count": len(messages),
            "average_importance": avg_importance,
            "segment_count": len(segments),
            "topics": topic_names,
            "high_importance_count": sum(
                1 for s in segments if s.importance_score > 0.7
            )
        }
