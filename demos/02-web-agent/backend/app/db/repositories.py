"""
数据库仓储
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from app.db.connection import get_pool


class User:
    """用户模型"""
    def __init__(
        self,
        id: str,
        username: str,
        password_hash: str,
        created_at: datetime
    ):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.created_at = created_at


class Session:
    """会话模型"""
    def __init__(
        self,
        id: str,
        user_id: str,
        created_at: datetime,
        updated_at: datetime
    ):
        self.id = id
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at


class Message:
    """消息模型"""
    def __init__(
        self,
        id: str,
        session_id: str,
        role: str,
        content: str,
        created_at: datetime,
        tool_calls: Optional[dict] = None
    ):
        self.id = id
        self.session_id = session_id
        self.role = role
        self.content = content
        self.created_at = created_at
        self.tool_calls = tool_calls


class UserRepository:
    """用户仓储"""

    async def create(self, username: str, password_hash: str) -> User:
        """创建用户"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                INSERT INTO users (username, password_hash)
                VALUES ($1, $2)
                RETURNING id, username, password_hash, created_at
                """,
                username, password_hash
            )

            return User(
                id=str(record['id']),
                username=record['username'],
                password_hash=record['password_hash'],
                created_at=record['created_at']
            )

    async def find_by_username(self, username: str) -> Optional[User]:
        """根据用户名查找用户"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                SELECT id, username, password_hash, created_at
                FROM users
                WHERE username = $1
                """,
                username
            )

            if not record:
                return None

            return User(
                id=str(record['id']),
                username=record['username'],
                password_hash=record['password_hash'],
                created_at=record['created_at']
            )

    async def find_by_id(self, user_id: str) -> Optional[User]:
        """根据 ID 查找用户"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                SELECT id, username, password_hash, created_at
                FROM users
                WHERE id = $1
                """,
                user_id
            )

            if not record:
                return None

            return User(
                id=str(record['id']),
                username=record['username'],
                password_hash=record['password_hash'],
                created_at=record['created_at']
            )


class SessionRepository:
    """会话仓储"""

    async def create(self, user_id: str) -> Session:
        """创建会话"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                INSERT INTO sessions (user_id)
                VALUES ($1)
                RETURNING id, user_id, created_at, updated_at
                """,
                user_id
            )

            return Session(
                id=str(record['id']),
                user_id=str(record['user_id']),
                created_at=record['created_at'],
                updated_at=record['updated_at']
            )

    async def find_by_id(self, session_id: str) -> Optional[Session]:
        """根据 ID 查找会话"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                SELECT id, user_id, created_at, updated_at
                FROM sessions
                WHERE id = $1
                """,
                session_id
            )

            if not record:
                return None

            return Session(
                id=str(record['id']),
                user_id=str(record['user_id']),
                created_at=record['created_at'],
                updated_at=record['updated_at']
            )

    async def find_by_user_id(self, user_id: str) -> List[Session]:
        """根据用户 ID 查找会话列表"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            records = await conn.fetch(
                """
                SELECT id, user_id, created_at, updated_at
                FROM sessions
                WHERE user_id = $1
                ORDER BY updated_at DESC
                """,
                user_id
            )

            return [
                Session(
                    id=str(record['id']),
                    user_id=str(record['user_id']),
                    created_at=record['created_at'],
                    updated_at=record['updated_at']
                )
                for record in records
            ]

    async def update(self, session_id: str) -> Session:
        """更新会话时间戳"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                UPDATE sessions
                SET updated_at = NOW()
                WHERE id = $1
                RETURNING id, user_id, created_at, updated_at
                """,
                session_id
            )

            return Session(
                id=str(record['id']),
                user_id=str(record['user_id']),
                created_at=record['created_at'],
                updated_at=record['updated_at']
            )

    async def delete(self, session_id: str) -> bool:
        """删除会话"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM sessions WHERE id = $1",
                session_id
            )
            return "DELETE 1" in result


class MessageRepository:
    """消息仓储"""

    async def create(
        self,
        session_id: str,
        role: str,
        content: str,
        tool_calls: Optional[dict] = None
    ) -> Message:
        """创建消息"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                INSERT INTO messages (session_id, role, content, tool_calls)
                VALUES ($1, $2, $3, $4)
                RETURNING id, session_id, role, content, tool_calls, created_at
                """,
                session_id, role, content, tool_calls
            )

            return Message(
                id=str(record['id']),
                session_id=str(record['session_id']),
                role=record['role'],
                content=record['content'],
                created_at=record['created_at'],
                tool_calls=record['tool_calls']
            )

    async def find_by_session_id(self, session_id: str) -> List[Message]:
        """根据会话 ID 查找消息"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            records = await conn.fetch(
                """
                SELECT id, session_id, role, content, tool_calls, created_at
                FROM messages
                WHERE session_id = $1
                ORDER BY created_at ASC
                """,
                session_id
            )

            return [
                Message(
                    id=str(record['id']),
                    session_id=str(record['session_id']),
                    role=record['role'],
                    content=record['content'],
                    created_at=record['created_at'],
                    tool_calls=record['tool_calls']
                )
                for record in records
            ]

    async def delete_by_session_id(self, session_id: str) -> bool:
        """删除会话的所有消息"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM messages WHERE session_id = $1",
                session_id
            )
            return "DELETE" in result
