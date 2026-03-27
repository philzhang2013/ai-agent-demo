"""
ImportanceScoreRepository 测试
TDD: 先写测试，再实现代码
用于更新和管理消息的重要性分数
"""
import pytest
from uuid import uuid4

from app.db.repositories import ImportanceScoreRepository, MessageRepository
from app.db.repositories import SessionRepository, UserRepository


class TestImportanceScoreRepository:
    """测试 ImportanceScoreRepository"""

    @pytest.fixture
    async def repo(self):
        """创建仓储实例"""
        return ImportanceScoreRepository()

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
    async def test_message(self, test_session):
        """创建测试消息"""
        msg_repo = MessageRepository()
        return await msg_repo.create(
            session_id=test_session.id,
            role="user",
            content="测试消息内容"
        )

    @pytest.mark.asyncio
    async def test_update_importance_score(self, repo, test_message):
        """测试更新消息重要性分数"""
        # Act
        result = await repo.update_score(
            message_id=test_message.id,
            importance_score=0.95
        )

        # Assert
        assert result is True

        # 验证更新成功
        updated = await repo.get_score(test_message.id)
        assert updated == 0.95

    @pytest.mark.asyncio
    async def test_update_importance_score_with_topic(self, repo, test_message):
        """测试同时更新重要性分数和主题标签"""
        # Act
        result = await repo.update_score(
            message_id=test_message.id,
            importance_score=0.88,
            topic_tag="AI技术"
        )

        # Assert
        assert result is True

        # 验证两者都更新成功
        score, topic = await repo.get_score_and_topic(test_message.id)
        assert score == 0.88
        assert topic == "AI技术"

    @pytest.mark.asyncio
    async def test_batch_update_scores(self, repo, test_session):
        """测试批量更新多个消息的重要性分数"""
        # Arrange - 创建多条消息
        msg_repo = MessageRepository()
        messages = []
        for i in range(5):
            msg = await msg_repo.create(
                session_id=test_session.id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"消息 {i}"
            )
            messages.append(msg)

        # 准备批量更新数据
        updates = [
            (messages[0].id, 0.9),
            (messages[1].id, 0.7),
            (messages[2].id, 0.85),
            (messages[3].id, 0.5),
            (messages[4].id, 0.95),
        ]

        # Act
        result = await repo.batch_update_scores(updates)

        # Assert
        assert result == 5  # 更新了 5 条记录

        # 验证更新结果
        for msg_id, expected_score in updates:
            actual_score = await repo.get_score(msg_id)
            assert actual_score == expected_score

    @pytest.mark.asyncio
    async def test_get_score_not_set(self, repo, test_message):
        """测试获取未设置的重要性分数（返回默认值）"""
        # Act
        score = await repo.get_score(test_message.id)

        # Assert - 默认值是 0.5
        assert score == 0.5

    @pytest.mark.asyncio
    async def test_get_high_importance_messages(self, repo, test_session):
        """测试获取高重要性消息"""
        # Arrange - 创建不同重要性的消息
        msg_repo = MessageRepository()

        high_importance_msg = await msg_repo.create(
            session_id=test_session.id,
            role="user",
            content="重要消息"
        )
        await repo.update_score(high_importance_msg.id, 0.9)

        low_importance_msg = await msg_repo.create(
            session_id=test_session.id,
            role="user",
            content="普通消息"
        )
        await repo.update_score(low_importance_msg.id, 0.3)

        medium_importance_msg = await msg_repo.create(
            session_id=test_session.id,
            role="assistant",
            content="一般消息"
        )
        await repo.update_score(medium_importance_msg.id, 0.6)

        # Act - 获取重要性 >= 0.8 的消息
        high_importance_messages = await repo.get_messages_by_importance_threshold(
            session_id=test_session.id,
            min_importance=0.8
        )

        # Assert
        assert len(high_importance_messages) == 1
        assert high_importance_messages[0][0] == high_importance_msg.id  # (id, score, content)
        assert high_importance_messages[0][1] == 0.9

    @pytest.mark.asyncio
    async def test_update_embedding(self, repo, test_message):
        """测试更新消息向量嵌入"""
        # Arrange
        embedding = [0.1] * 2048  # 2048 维向量（智谱 embedding-3）

        # Act
        result = await repo.update_embedding(
            message_id=test_message.id,
            embedding=embedding
        )

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_get_messages_without_embedding(self, repo, test_session):
        """测试获取没有向量嵌入的消息"""
        # Arrange - 创建消息，一个带 embedding，一个不带
        msg_repo = MessageRepository()

        msg_without_embedding = await msg_repo.create(
            session_id=test_session.id,
            role="user",
            content="无向量消息"
        )

        msg_with_embedding = await msg_repo.create(
            session_id=test_session.id,
            role="assistant",
            content="有向量消息"
        )
        await repo.update_embedding(msg_with_embedding.id, [0.1] * 2048)

        # Act
        messages_without_embedding = await repo.get_messages_without_embedding(
            session_id=test_session.id,
            limit=10
        )

        # Assert
        assert len(messages_without_embedding) == 1
        assert messages_without_embedding[0]['id'] == msg_without_embedding.id
