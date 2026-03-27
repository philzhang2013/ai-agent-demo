"""
MemorySegmentRepository 测试
TDD: 先写测试，再实现代码
"""
import pytest
from uuid import uuid4
from datetime import datetime

from app.db.repositories import MemorySegmentRepository, MemorySegment
from app.db.repositories import SessionRepository, UserRepository
from app.db.connection import get_pool


class TestMemorySegmentRepository:
    """测试 MemorySegmentRepository"""

    @pytest.fixture
    async def repo(self):
        """创建仓储实例"""
        return MemorySegmentRepository()

    @pytest.fixture
    async def test_user(self):
        """创建测试用户"""
        user_repo = UserRepository()
        import hashlib
        password_hash = hashlib.sha256("test_password".encode()).hexdigest()
        return await user_repo.create(
            username=f"test_user_{uuid4().hex[:8]}",
            password_hash=password_hash
        )

    @pytest.fixture
    async def test_session(self, test_user):
        """创建测试会话"""
        session_repo = SessionRepository()
        return await session_repo.create(
            user_id=test_user.id,
            title="Test Session"
        )

    @pytest.fixture
    async def test_messages(self, test_session):
        """创建测试消息用于构建主题段"""
        from app.db.repositories import MessageRepository
        msg_repo = MessageRepository()

        messages = []
        for i in range(5):
            msg = await msg_repo.create(
                session_id=test_session.id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Test message {i}"
            )
            messages.append(msg)
        return messages

    @pytest.mark.asyncio
    async def test_create_memory_segment(self, repo, test_session, test_messages):
        """测试创建记忆主题段"""
        # Arrange
        segment = await repo.create(
            session_id=test_session.id,
            topic_name="测试主题",
            start_message_id=test_messages[0].id,
            end_message_id=test_messages[-1].id,
            summary_content="这是一个测试摘要",
            importance_score=0.85,
            message_count=5,
            total_importance=4.25
        )

        # Assert
        assert segment is not None
        assert segment.session_id == test_session.id
        assert segment.topic_name == "测试主题"
        assert segment.start_message_id == test_messages[0].id
        assert segment.end_message_id == test_messages[-1].id
        assert segment.summary_content == "这是一个测试摘要"
        assert segment.importance_score == 0.85
        assert segment.message_count == 5
        assert segment.total_importance == 4.25
        assert segment.id is not None
        assert segment.created_at is not None
        assert segment.updated_at is not None

    @pytest.mark.asyncio
    async def test_find_by_session_id(self, repo, test_session, test_messages):
        """测试根据会话 ID 查找主题段"""
        # Arrange - 创建两个主题段
        await repo.create(
            session_id=test_session.id,
            topic_name="主题1",
            start_message_id=test_messages[0].id,
            end_message_id=test_messages[1].id,
            summary_content="摘要1",
            importance_score=0.8,
            message_count=2,
            total_importance=1.6
        )
        await repo.create(
            session_id=test_session.id,
            topic_name="主题2",
            start_message_id=test_messages[2].id,
            end_message_id=test_messages[-1].id,
            summary_content="摘要2",
            importance_score=0.9,
            message_count=3,
            total_importance=2.7
        )

        # Act
        segments = await repo.find_by_session_id(test_session.id)

        # Assert
        assert len(segments) == 2
        assert all(isinstance(s, MemorySegment) for s in segments)
        assert segments[0].topic_name == "主题1"
        assert segments[1].topic_name == "主题2"

    @pytest.mark.asyncio
    async def test_find_by_id(self, repo, test_session, test_messages):
        """测试根据 ID 查找主题段"""
        # Arrange
        created = await repo.create(
            session_id=test_session.id,
            topic_name="测试主题",
            start_message_id=test_messages[0].id,
            end_message_id=test_messages[-1].id,
            summary_content="测试摘要",
            importance_score=0.75,
            message_count=5,
            total_importance=3.75
        )

        # Act
        found = await repo.find_by_id(created.id)

        # Assert
        assert found is not None
        assert found.id == created.id
        assert found.topic_name == "测试主题"
        assert found.summary_content == "测试摘要"

    @pytest.mark.asyncio
    async def test_find_by_id_not_found(self, repo):
        """测试查找不存在的主题段"""
        # Act
        found = await repo.find_by_id(str(uuid4()))

        # Assert
        assert found is None

    @pytest.mark.asyncio
    async def test_update(self, repo, test_session, test_messages):
        """测试更新主题段"""
        # Arrange
        created = await repo.create(
            session_id=test_session.id,
            topic_name="旧主题",
            start_message_id=test_messages[0].id,
            end_message_id=test_messages[-1].id,
            summary_content="旧摘要",
            importance_score=0.5,
            message_count=5,
            total_importance=2.5
        )

        # Act
        updated = await repo.update(
            segment_id=created.id,
            topic_name="新主题",
            summary_content="新摘要",
            importance_score=0.95
        )

        # Assert
        assert updated is not None
        assert updated.topic_name == "新主题"
        assert updated.summary_content == "新摘要"
        assert updated.importance_score == 0.95
        assert updated.id == created.id
        # updated_at 应该被更新
        assert updated.updated_at >= created.updated_at

    @pytest.mark.asyncio
    async def test_delete(self, repo, test_session, test_messages):
        """测试删除主题段"""
        # Arrange
        created = await repo.create(
            session_id=test_session.id,
            topic_name="待删除主题",
            start_message_id=test_messages[0].id,
            end_message_id=test_messages[-1].id,
            summary_content="待删除摘要",
            importance_score=0.6,
            message_count=5,
            total_importance=3.0
        )

        # Act
        result = await repo.delete(created.id)

        # Assert
        assert result is True
        found = await repo.find_by_id(created.id)
        assert found is None

    @pytest.mark.asyncio
    async def test_find_by_importance_threshold(self, repo, test_session, test_messages):
        """测试根据重要性阈值查找主题段"""
        # Arrange - 创建不同重要性的主题段
        await repo.create(
            session_id=test_session.id,
            topic_name="高重要性主题",
            start_message_id=test_messages[0].id,
            end_message_id=test_messages[1].id,
            summary_content="高重要性摘要",
            importance_score=0.9,
            message_count=2,
            total_importance=1.8
        )
        await repo.create(
            session_id=test_session.id,
            topic_name="低重要性主题",
            start_message_id=test_messages[2].id,
            end_message_id=test_messages[-1].id,
            summary_content="低重要性摘要",
            importance_score=0.3,
            message_count=3,
            total_importance=0.9
        )

        # Act - 查找重要性 >= 0.8 的主题段
        segments = await repo.find_by_importance_threshold(
            session_id=test_session.id,
            min_importance=0.8
        )

        # Assert
        assert len(segments) == 1
        assert segments[0].topic_name == "高重要性主题"
        assert segments[0].importance_score >= 0.8

    @pytest.mark.asyncio
    async def test_semantic_search(self, repo, test_session, test_messages):
        """测试语义搜索（使用向量相似度）"""
        # Arrange - 创建带向量的主题段
        # 使用 2048 维的零向量作为测试（智谱 embedding-3）
        embedding = [0.0] * 2048
        await repo.create(
            session_id=test_session.id,
            topic_name="AI 技术讨论",
            start_message_id=test_messages[0].id,
            end_message_id=test_messages[-1].id,
            summary_content="关于人工智能的讨论",
            importance_score=0.8,
            embedding=embedding,
            message_count=5,
            total_importance=4.0
        )

        # Act - 使用相同的向量进行搜索
        segments = await repo.semantic_search(
            session_id=test_session.id,
            query_embedding=embedding,
            limit=5
        )

        # Assert
        assert len(segments) >= 1
        assert all(isinstance(s, MemorySegment) for s in segments)
