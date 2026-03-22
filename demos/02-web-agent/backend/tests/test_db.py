"""
数据库模块测试
"""
import pytest
from datetime import datetime
from uuid import uuid4

from app.db.connection import get_connection
from app.db.repositories import (
    UserRepository,
    SessionRepository,
    MessageRepository
)
from app.auth.password import hash_password


class TestUserRepository:
    """测试用户仓储"""

    @pytest.mark.asyncio
    async def test_should_create_user(self):
        """测试应该创建用户"""
        repo = UserRepository()
        password_hash = hash_password("password123")

        user = await repo.create("testuser", password_hash)

        assert user.id is not None
        assert user.username == "testuser"
        assert user.password_hash == password_hash
        assert user.created_at is not None

    @pytest.mark.asyncio
    async def test_should_find_user_by_username(self):
        """测试应该根据用户名查找用户"""
        repo = UserRepository()
        password_hash = hash_password("password123")

        created = await repo.create("testuser", password_hash)
        found = await repo.find_by_username("testuser")

        assert found is not None
        assert found.id == created.id
        assert found.username == "testuser"

    @pytest.mark.asyncio
    async def test_return_none_for_nonexistent_user(self):
        """测试不存在的用户应该返回 None"""
        repo = UserRepository()
        found = await repo.find_by_username("nonexistent")

        assert found is None

    @pytest.mark.asyncio
    async def test_should_find_user_by_id(self):
        """测试应该根据 ID 查找用户"""
        repo = UserRepository()
        password_hash = hash_password("password123")

        created = await repo.create("testuser", password_hash)
        found = await repo.find_by_id(created.id)

        assert found is not None
        assert found.username == "testuser"


class TestSessionRepository:
    """测试会话仓储"""

    @pytest.mark.asyncio
    async def test_should_create_session(self):
        """测试应该创建会话"""
        user_repo = UserRepository()
        session_repo = SessionRepository()

        password_hash = hash_password("password123")
        user = await user_repo.create("testuser", password_hash)

        session = await session_repo.create(user.id)

        assert session.id is not None
        assert session.user_id == user.id
        assert session.created_at is not None

    @pytest.mark.asyncio
    async def test_should_find_sessions_by_user_id(self):
        """测试应该根据用户 ID 查找会话"""
        user_repo = UserRepository()
        session_repo = SessionRepository()

        password_hash = hash_password("password123")
        user = await user_repo.create("testuser", password_hash)

        await session_repo.create(user.id)
        await session_repo.create(user.id)

        sessions = await session_repo.find_by_user_id(user.id)

        assert len(sessions) == 2

    @pytest.mark.asyncio
    async def test_should_find_session_by_id(self):
        """测试应该根据 ID 查找会话"""
        user_repo = UserRepository()
        session_repo = SessionRepository()

        password_hash = hash_password("password123")
        user = await user_repo.create("testuser", password_hash)

        created = await session_repo.create(user.id)
        found = await session_repo.find_by_id(created.id)

        assert found is not None
        assert found.id == created.id

    @pytest.mark.asyncio
    async def test_should_delete_session(self):
        """测试应该删除会话"""
        user_repo = UserRepository()
        session_repo = SessionRepository()

        password_hash = hash_password("password123")
        user = await user_repo.create("testuser", password_hash)

        session = await session_repo.create(user.id)
        await session_repo.delete(session.id)

        found = await session_repo.find_by_id(session.id)
        assert found is None


class TestMessageRepository:
    """测试消息仓储"""

    @pytest.mark.asyncio
    async def test_should_create_message(self):
        """测试应该创建消息"""
        user_repo = UserRepository()
        session_repo = SessionRepository()
        message_repo = MessageRepository()

        password_hash = hash_password("password123")
        user = await user_repo.create("testuser", password_hash)
        session = await session_repo.create(user.id)

        message = await message_repo.create(
            session.id,
            "user",
            "Hello"
        )

        assert message.id is not None
        assert message.session_id == session.id
        assert message.role == "user"
        assert message.content == "Hello"

    @pytest.mark.asyncio
    async def test_should_find_messages_by_session_id(self):
        """测试应该根据会话 ID 查找消息"""
        user_repo = UserRepository()
        session_repo = SessionRepository()
        message_repo = MessageRepository()

        password_hash = hash_password("password123")
        user = await user_repo.create("testuser", password_hash)
        session = await session_repo.create(user.id)

        await message_repo.create(session.id, "user", "Hello")
        await message_repo.create(session.id, "assistant", "Hi there")

        messages = await message_repo.find_by_session_id(session.id)

        assert len(messages) == 2
        assert messages[0].role == "user"
        assert messages[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_should_delete_messages_by_session_id(self):
        """测试应该删除会话的所有消息"""
        user_repo = UserRepository()
        session_repo = SessionRepository()
        message_repo = MessageRepository()

        password_hash = hash_password("password123")
        user = await user_repo.create("testuser", password_hash)
        session = await session_repo.create(user.id)

        await message_repo.create(session.id, "user", "Hello")
        await message_repo.create(session.id, "assistant", "Hi")

        await message_repo.delete_by_session_id(session.id)

        messages = await message_repo.find_by_session_id(session.id)
        assert len(messages) == 0
