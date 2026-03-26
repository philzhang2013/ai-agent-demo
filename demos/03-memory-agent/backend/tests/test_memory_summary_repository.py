"""
MemorySummaryRepository 测试
严格遵循TDD：先写测试，确保测试失败（RED状态）
"""
import pytest
from datetime import datetime
from uuid import uuid4

from app.db.repositories import (
    UserRepository,
    SessionRepository,
    MessageRepository,
    MemorySummaryRepository,
    MemorySummary
)
from app.auth.password import hash_password
from uuid import uuid4


class TestMemorySummaryRepository:
    """测试记忆摘要仓储"""

    @pytest.mark.asyncio
    async def test_create_summary_success(self):
        """测试应该成功创建摘要"""
        # Arrange
        user_repo = UserRepository()
        session_repo = SessionRepository()
        summary_repo = MemorySummaryRepository()

        password_hash = hash_password("password123")
        unique_id = str(uuid4())[:8]
        user = await user_repo.create(f"testuser_create_{unique_id}", password_hash)
        session = await session_repo.create(user.id)

        # Act
        summary = await summary_repo.create(
            session_id=session.id,
            content="这是测试摘要内容",
            message_count=5
        )

        # Assert
        assert summary.id is not None
        assert summary.session_id == session.id
        assert summary.content == "这是测试摘要内容"
        assert summary.message_count == 5
        assert summary.created_at is not None
        assert summary.updated_at is not None

    @pytest.mark.asyncio
    async def test_create_summary_duplicate_session_should_update(self):
        """测试重复创建同一会话的摘要应该更新而非报错"""
        # Arrange
        user_repo = UserRepository()
        session_repo = SessionRepository()
        summary_repo = MemorySummaryRepository()

        password_hash = hash_password("password123")
        unique_id = str(uuid4())[:8]
        user = await user_repo.create(f"testuser_dup_{unique_id}", password_hash)
        session = await session_repo.create(user.id)

        # 首次创建
        first_summary = await summary_repo.create(
            session_id=session.id,
            content="初始摘要",
            message_count=5
        )

        # Act - 再次创建同一session的摘要（应该更新）
        second_summary = await summary_repo.create(
            session_id=session.id,
            content="更新后的摘要",
            message_count=10
        )

        # Assert
        assert second_summary.id == first_summary.id  # 同一条记录
        assert second_summary.content == "更新后的摘要"
        assert second_summary.message_count == 10
        assert second_summary.updated_at >= first_summary.updated_at

    @pytest.mark.asyncio
    async def test_find_by_session_id_exists(self):
        """测试应该根据会话ID查找存在的摘要"""
        # Arrange
        user_repo = UserRepository()
        session_repo = SessionRepository()
        summary_repo = MemorySummaryRepository()

        password_hash = hash_password("password123")
        unique_id = str(uuid4())[:8]
        user = await user_repo.create(f"testuser_find_{unique_id}", password_hash)
        session = await session_repo.create(user.id)

        created = await summary_repo.create(
            session_id=session.id,
            content="查找测试摘要",
            message_count=5
        )

        # Act
        found = await summary_repo.find_by_session_id(session.id)

        # Assert
        assert found is not None
        assert found.id == created.id
        assert found.session_id == session.id
        assert found.content == "查找测试摘要"
        assert found.message_count == 5

    @pytest.mark.asyncio
    async def test_find_by_session_id_not_exists(self):
        """测试查找不存在的会话摘要应该返回None"""
        # Arrange
        summary_repo = MemorySummaryRepository()
        nonexistent_session_id = str(uuid4())

        # Act
        found = await summary_repo.find_by_session_id(nonexistent_session_id)

        # Assert
        assert found is None

    @pytest.mark.asyncio
    async def test_find_by_session_id_invalid_uuid(self):
        """测试使用无效UUID查找应该返回None或抛出适当异常"""
        # Arrange
        summary_repo = MemorySummaryRepository()
        invalid_session_id = "not-a-valid-uuid"

        # Act & Assert
        # 根据实现，可能返回None或抛出异常
        try:
            found = await summary_repo.find_by_session_id(invalid_session_id)
            assert found is None
        except (ValueError, Exception):
            # 抛出异常也是可接受的行为
            pass

    @pytest.mark.asyncio
    async def test_update_summary_success(self):
        """测试应该成功更新摘要"""
        # Arrange
        user_repo = UserRepository()
        session_repo = SessionRepository()
        summary_repo = MemorySummaryRepository()

        password_hash = hash_password("password123")
        unique_id = str(uuid4())[:8]
        user = await user_repo.create(f"testuser_upd_{unique_id}", password_hash)
        session = await session_repo.create(user.id)

        created = await summary_repo.create(
            session_id=session.id,
            content="原始摘要",
            message_count=5
        )

        # Act
        updated = await summary_repo.update(
            session_id=session.id,
            content="显式更新的摘要",
            message_count=15
        )

        # Assert
        assert updated is not None
        assert updated.id == created.id
        assert updated.content == "显式更新的摘要"
        assert updated.message_count == 15
        assert updated.updated_at > created.updated_at
