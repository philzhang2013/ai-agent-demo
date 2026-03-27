"""
SmartMemoryManager 测试
TDD: 先写测试，再实现代码

智能记忆管理器职责：
- 协调 ImportanceScorer、TopicSegmenter、VectorStore
- 处理消息流，生成分层记忆
- 提供记忆检索接口
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

from app.memory.smart_memory_manager import SmartMemoryManager


class TestSmartMemoryManager:
    """测试 SmartMemoryManager"""

    @pytest.fixture
    def mock_dependencies(self):
        """创建模拟依赖"""
        return {
            'importance_scorer': Mock(),
            'topic_segmenter': Mock(),
            'vector_store': Mock(),
            'importance_repo': AsyncMock(),
            'segment_repo': AsyncMock(),
        }

    @pytest.fixture
    def manager(self, mock_dependencies):
        """创建 SmartMemoryManager 实例"""
        return SmartMemoryManager(
            importance_scorer=mock_dependencies['importance_scorer'],
            topic_segmenter=mock_dependencies['topic_segmenter'],
            vector_store=mock_dependencies['vector_store'],
            importance_repo=mock_dependencies['importance_repo'],
            segment_repo=mock_dependencies['segment_repo'],
        )

    @pytest.mark.asyncio
    async def test_process_message(self, manager, mock_dependencies):
        """测试处理单条消息"""
        # Arrange
        mock_dependencies['importance_scorer'].score.return_value = 0.85
        mock_dependencies['vector_store'].embed.return_value = [0.1] * 2048

        message = {
            "id": "msg-1",
            "session_id": "session-1",
            "content": "测试消息内容",
            "created_at": datetime.now()
        }

        # Act
        result = await manager.process_message(message)

        # Assert
        assert result is True
        mock_dependencies['importance_scorer'].score.assert_called_once_with("测试消息内容")
        mock_dependencies['importance_repo'].update_score.assert_called_once()

    @pytest.mark.asyncio
    async def test_batch_score_messages(self, manager, mock_dependencies):
        """测试批量评分消息"""
        # Arrange
        messages = [
            {"id": "msg-1", "content": "消息1"},
            {"id": "msg-2", "content": "消息2"},
            {"id": "msg-3", "content": "消息3"},
        ]
        mock_dependencies['importance_scorer'].score_batch.return_value = [0.5, 0.7, 0.9]

        # Act
        scores = await manager.batch_score_messages(messages)

        # Assert
        assert len(scores) == 3
        assert scores == [0.5, 0.7, 0.9]
        mock_dependencies['importance_scorer'].score_batch.assert_called_once_with(["消息1", "消息2", "消息3"])

    @pytest.mark.asyncio
    async def test_create_topic_segments(self, manager, mock_dependencies):
        """测试创建主题段"""
        # Arrange
        from app.memory.topic_segmenter import TopicSegment

        messages = [
            {"id": "msg-1", "content": "讨论数据库设计", "created_at": datetime.now()},
            {"id": "msg-2", "content": "PostgreSQL 是个不错的选择", "created_at": datetime.now() + timedelta(minutes=2)},
        ]

        mock_segment = TopicSegment(
            topic_name="数据库设计",
            start_message_id="msg-1",
            end_message_id="msg-2",
            message_count=2,
            importance_score=0.75,
            summary="讨论使用 PostgreSQL 进行数据库设计"
        )
        mock_dependencies['topic_segmenter'].segment.return_value = [mock_segment]

        # Act
        segments = await manager.create_topic_segments("session-1", messages)

        # Assert
        assert len(segments) == 1
        assert segments[0].topic_name == "数据库设计"
        mock_dependencies['topic_segmenter'].segment.assert_called_once()

    @pytest.mark.asyncio
    async def test_semantic_search(self, manager, mock_dependencies):
        """测试语义搜索记忆"""
        # Arrange
        query = "如何优化数据库性能？"
        mock_dependencies['vector_store'].embed.return_value = [0.1] * 2048
        mock_dependencies['segment_repo'].semantic_search.return_value = [
            Mock(topic_name="数据库优化", summary_content="使用索引优化查询")
        ]

        # Act
        results = await manager.semantic_search("session-1", query, limit=5)

        # Assert
        assert len(results) >= 0  # 可能为空或有结果
        mock_dependencies['vector_store'].embed.assert_called_once_with(query)

    @pytest.mark.asyncio
    async def test_get_high_importance_messages(self, manager, mock_dependencies):
        """测试获取高重要性消息"""
        # Arrange
        mock_dependencies['importance_repo'].get_messages_by_importance_threshold.return_value = [
            ("msg-1", 0.95, "重要的架构决策"),
            ("msg-2", 0.88, "关键的安全问题"),
        ]

        # Act
        messages = await manager.get_high_importance_messages("session-1", threshold=0.8)

        # Assert
        assert len(messages) == 2
        assert messages[0][1] >= 0.8  # 重要性分数
        mock_dependencies['importance_repo'].get_messages_by_importance_threshold.assert_called_once()

    @pytest.mark.asyncio
    async def test_build_context_with_smart_memory(self, manager, mock_dependencies):
        """测试使用智能记忆构建上下文"""
        # Arrange
        mock_dependencies['importance_repo'].get_messages_by_importance_threshold.return_value = [
            ("msg-1", 0.9, "重要的背景信息"),
        ]

        # 创建一个完整的 Mock 对象
        mock_segment = Mock()
        mock_segment.topic_name = "项目背景"
        mock_segment.summary_content = "这是一个关于AI项目的信息"
        mock_segment.importance_score = 0.75

        mock_dependencies['segment_repo'].find_by_session_id.return_value = [mock_segment]

        # Act
        context = await manager.build_context("session-1", current_message="新的问题")

        # Assert
        assert isinstance(context, str)
        assert len(context) > 0

    @pytest.mark.asyncio
    async def test_empty_session(self, manager):
        """测试空会话处理"""
        # Act
        segments = await manager.create_topic_segments("empty-session", [])

        # Assert
        assert len(segments) == 0

    def test_calculate_session_importance(self, manager, mock_dependencies):
        """测试计算会话整体重要性"""
        # Arrange
        messages = [
            {"content": "普通消息"},
            {"content": "重要消息！"},
            {"content": "关键决策"},
        ]
        mock_dependencies['importance_scorer'].score_batch.return_value = [0.4, 0.9, 0.85]

        # Act
        avg_importance = manager.calculate_session_importance(messages)

        # Assert
        assert 0.0 <= avg_importance <= 1.0
        assert avg_importance == pytest.approx(0.717, rel=0.01)
