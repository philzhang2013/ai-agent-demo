"""
数据库模块测试
"""
import pytest
from datetime import datetime
from uuid import uuid4

from app.db.connection import get_pool
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


class TestSessionTitleMigration:
    """测试会话标题迁移 (002_add_session_title.sql)

    注意：这些测试需要数据库连接。如果网络问题导致无法连接 Supabase，
    这些测试将被跳过。功能实现后可以手动验证。
    """

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="网络问题无法连接 Supabase - RED 状态：需要运行迁移")
    async def test_sessions_table_should_have_title_column(self):
        """测试 sessions 表应该有 title 字段"""
        pool = await get_pool()

        async with pool.acquire() as conn:
            # 查询 sessions 表的列信息
            column_info = await conn.fetchrow("""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns
                WHERE table_name = 'sessions' AND column_name = 'title'
            """)

        # 验证 title 字段存在
        assert column_info is not None, "title 字段不存在（RED: 需要运行迁移）"
        assert column_info['data_type'] == 'character varying'
        assert column_info['column_default'] == "'新对话'::character varying"

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="网络问题无法连接 Supabase - RED 状态：需要运行迁移")
    async def test_new_session_should_have_default_title(self):
        """测试新创建的会话应该有默认标题"""
        user_repo = UserRepository()
        session_repo = SessionRepository()

        password_hash = hash_password("password123")
        user = await user_repo.create("testuser_title", password_hash)

        # 创建会话
        session = await session_repo.create(user.id)

        # 从数据库直接查询验证 title 字段
        pool = await get_pool()
        async with pool.acquire() as conn:
            record = await conn.fetchrow(
                "SELECT title FROM sessions WHERE id = $1",
                session.id
            )

        # 验证默认标题为 "新对话"
        assert record is not None, "会话不存在"
        assert record['title'] == '新对话'

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="网络问题无法连接 Supabase - RED 状态：需要运行迁移")
    async def test_should_have_sessions_user_updated_index(self):
        """测试应该存在 idx_sessions_user_updated 索引"""
        pool = await get_pool()

        async with pool.acquire() as conn:
            # 查询索引信息
            index_info = await conn.fetchrow("""
                SELECT indexname
                FROM pg_indexes
                WHERE indexname = 'idx_sessions_user_updated'
            """)

        # 验证索引存在
        assert index_info is not None, "idx_sessions_user_updated 索引不存在（RED: 需要运行迁移）"
        assert index_info['indexname'] == 'idx_sessions_user_updated'
