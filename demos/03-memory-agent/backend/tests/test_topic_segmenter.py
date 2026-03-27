"""
TopicSegmenter 测试
TDD: 先写测试，再实现代码

主题分段逻辑：
- LLM 判断主题切换
- 相似度低于阈值 → 触发新段
- 固定时间间隔 → 强制分段
"""
import pytest
from datetime import datetime, timedelta
from app.memory.topic_segmenter import TopicSegmenter, TopicSegment


class TestTopicSegmenter:
    """测试 TopicSegmenter"""

    @pytest.fixture
    def segmenter(self):
        """创建分割器实例"""
        return TopicSegmenter(
            similarity_threshold=0.7,
            max_segment_messages=5,
            max_segment_duration=timedelta(minutes=30)
        )

    def test_single_segment(self, segmenter):
        """测试单条消息创建主题段"""
        # Arrange
        messages = [
            {"id": "1", "content": "让我们讨论数据库设计", "created_at": datetime.now()}
        ]

        # Act
        segments = segmenter.segment(messages)

        # Assert
        assert len(segments) == 1
        assert segments[0].topic_name == "数据库设计"
        assert segments[0].start_message_id == "1"
        assert segments[0].end_message_id == "1"

    def test_topic_switch_detection(self, segmenter):
        """测试主题切换检测"""
        # Arrange - 两条明显不同主题的消息
        messages = [
            {"id": "1", "content": "Python 的列表推导式很强大", "created_at": datetime.now()},
            {"id": "2", "content": "说到食物，我推荐意大利面", "created_at": datetime.now() + timedelta(minutes=1)},
        ]

        # Act
        segments = segmenter.segment(messages)

        # Assert - 应该分成两个主题段
        assert len(segments) == 2

    def test_similar_topic_merge(self, segmenter):
        """测试相似主题合并"""
        # Arrange - 相似主题的消息
        messages = [
            {"id": "1", "content": "如何优化 PostgreSQL 查询性能？", "created_at": datetime.now()},
            {"id": "2", "content": "PostgreSQL 的索引策略有哪些？", "created_at": datetime.now() + timedelta(minutes=2)},
            {"id": "3", "content": "EXPLAIN ANALYZE 如何解读？", "created_at": datetime.now() + timedelta(minutes=4)},
        ]

        # Act
        segments = segmenter.segment(messages)

        # Assert - 相似主题应该合并
        assert len(segments) == 1
        assert segments[0].start_message_id == "1"
        assert segments[0].end_message_id == "3"
        assert segments[0].message_count == 3

    def test_max_messages_limit(self, segmenter):
        """测试最大消息数限制触发分段"""
        # Arrange - 超过最大消息数的消息
        messages = [
            {"id": str(i), "content": f"消息内容 {i}", "created_at": datetime.now() + timedelta(minutes=i)}
            for i in range(7)  # 超过 max_segment_messages=5
        ]

        # Act
        segments = segmenter.segment(messages)

        # Assert - 应该分成多个段
        assert len(segments) >= 2
        # 每个段不超过最大消息数
        for segment in segments:
            assert segment.message_count <= 5

    def test_time_based_segmentation(self, segmenter):
        """测试基于时间的分段"""
        # Arrange - 时间间隔很大的消息
        now = datetime.now()
        messages = [
            {"id": "1", "content": "早上好，今天讨论 API 设计", "created_at": now},
            {"id": "2", "content": "下午继续，关于认证部分", "created_at": now + timedelta(minutes=35)},  # 超过30分钟
        ]

        # Act
        segments = segmenter.segment(messages)

        # Assert - 时间间隔过大应该分段
        assert len(segments) == 2

    def test_empty_messages(self, segmenter):
        """测试空消息列表"""
        segments = segmenter.segment([])
        assert len(segments) == 0

    def test_topic_name_extraction(self, segmenter):
        """测试主题名称提取"""
        messages = [
            {"id": "1", "content": "Redis 缓存穿透问题怎么解决？", "created_at": datetime.now()},
            {"id": "2", "content": "可以使用布隆过滤器", "created_at": datetime.now() + timedelta(minutes=1)},
        ]

        segments = segmenter.segment(messages)

        assert len(segments) == 1
        # 主题名应该从内容中提取关键词
        assert "Redis" in segments[0].topic_name or "缓存" in segments[0].topic_name

    def test_segment_summary_generation(self, segmenter):
        """测试主题段摘要生成"""
        messages = [
            {"id": "1", "content": "用户问：Python 的 GIL 是什么？", "created_at": datetime.now()},
            {"id": "2", "content": "助手答：GIL 是全局解释器锁", "created_at": datetime.now() + timedelta(minutes=1)},
        ]

        segments = segmenter.segment(messages)

        assert len(segments) == 1
        # 应该生成摘要
        assert len(segments[0].summary) > 0
        assert "GIL" in segments[0].summary or "全局解释器锁" in segments[0].summary

    def test_importance_calculation(self, segmenter):
        """测试主题段重要性计算"""
        messages = [
            {"id": "1", "content": "这是一个非常重要的架构决策！", "created_at": datetime.now()},
            {"id": "2", "content": "我们必须仔细考虑架构的扩展性", "created_at": datetime.now() + timedelta(minutes=1)},
        ]

        segments = segmenter.segment(messages)

        assert len(segments) == 1
        # 重要内容应该有较高分数
        assert segments[0].importance_score > 0.6
