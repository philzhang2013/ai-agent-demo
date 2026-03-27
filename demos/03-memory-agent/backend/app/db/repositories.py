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
        title: str,
        created_at: datetime,
        updated_at: datetime
    ):
        self.id = id
        self.user_id = user_id
        self.title = title
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


class SessionPreview:
    """会话预览模型（用于列表显示）"""
    def __init__(
        self,
        id: str,
        title: str,
        last_message: str,
        message_count: int,
        updated_at: datetime
    ):
        self.id = id
        self.title = title
        self.last_message = last_message
        self.message_count = message_count
        self.updated_at = updated_at


class MemorySummary:
    """记忆摘要模型"""
    def __init__(
        self,
        id: str,
        session_id: str,
        content: str,
        message_count: int,
        created_at: datetime,
        updated_at: datetime
    ):
        self.id = id
        self.session_id = session_id
        self.content = content
        self.message_count = message_count
        self.created_at = created_at
        self.updated_at = updated_at


class MemorySegment:
    """记忆主题段模型"""
    def __init__(
        self,
        id: str,
        session_id: str,
        topic_name: str,
        start_message_id: str,
        end_message_id: str,
        summary_content: str,
        importance_score: float,
        message_count: int,
        total_importance: float,
        created_at: datetime,
        updated_at: datetime,
        embedding: Optional[List[float]] = None
    ):
        self.id = id
        self.session_id = session_id
        self.topic_name = topic_name
        self.start_message_id = start_message_id
        self.end_message_id = end_message_id
        self.summary_content = summary_content
        self.importance_score = importance_score
        self.message_count = message_count
        self.total_importance = total_importance
        self.created_at = created_at
        self.updated_at = updated_at
        self.embedding = embedding


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

    async def create(self, user_id: str, title: str = "新对话") -> Session:
        """创建会话"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                INSERT INTO sessions (user_id, title)
                VALUES ($1, $2)
                RETURNING id, user_id, title, created_at, updated_at
                """,
                user_id, title
            )

            return Session(
                id=str(record['id']),
                user_id=str(record['user_id']),
                title=record['title'],
                created_at=record['created_at'],
                updated_at=record['updated_at']
            )

    async def find_by_id(self, session_id: str) -> Optional[Session]:
        """根据 ID 查找会话"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                SELECT id, user_id, title, created_at, updated_at
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
                title=record['title'],
                created_at=record['created_at'],
                updated_at=record['updated_at']
            )

    async def find_by_user_id(self, user_id: str) -> List[Session]:
        """根据用户 ID 查找会话列表"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            records = await conn.fetch(
                """
                SELECT id, user_id, title, created_at, updated_at
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
                    title=record['title'],
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
                RETURNING id, user_id, title, created_at, updated_at
                """,
                session_id
            )

            return Session(
                id=str(record['id']),
                user_id=str(record['user_id']),
                title=record['title'],
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

    async def update_title(self, session_id: str, title: str) -> Optional[Session]:
        """更新会话标题"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                UPDATE sessions
                SET title = $2, updated_at = NOW()
                WHERE id = $1
                RETURNING id, user_id, title, created_at, updated_at
                """,
                session_id, title
            )

            if not record:
                return None

            return Session(
                id=str(record['id']),
                user_id=str(record['user_id']),
                title=record['title'],
                created_at=record['created_at'],
                updated_at=record['updated_at']
            )

    async def find_with_preview(self, user_id: str) -> List[SessionPreview]:
        """获取会话列表（含最后一条消息预览）"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            records = await conn.fetch(
                """
                SELECT
                    s.id,
                    s.title,
                    s.updated_at,
                    COALESCE(m.content, '') as last_message,
                    COALESCE(m.message_count, 0) as message_count
                FROM sessions s
                LEFT JOIN (
                    SELECT
                        session_id,
                        content,
                        ROW_NUMBER() OVER (PARTITION BY session_id ORDER BY created_at DESC) as rn,
                        COUNT(*) as message_count
                    FROM messages
                    GROUP BY session_id, content, created_at
                ) m ON m.session_id = s.id AND m.rn = 1
                WHERE s.user_id = $1
                ORDER BY s.updated_at DESC
                """,
                user_id
            )

            return [
                SessionPreview(
                    id=str(record['id']),
                    title=record['title'],
                    last_message=record['last_message'],
                    message_count=record['message_count'],
                    updated_at=record['updated_at']
                )
                for record in records
            ]


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


class MemorySummaryRepository:
    """记忆摘要仓储"""

    async def create(
        self,
        session_id: str,
        content: str,
        message_count: int
    ) -> MemorySummary:
        """
        创建或更新记忆摘要
        如果 session_id 已存在，则更新现有记录
        """
        pool = await get_pool()
        async with pool.acquire() as conn:
            # 使用 PostgreSQL 的 UPSERT (ON CONFLICT DO UPDATE)
            record = await conn.fetchrow(
                """
                INSERT INTO memory_summaries (session_id, content, message_count)
                VALUES ($1, $2, $3)
                ON CONFLICT (session_id) DO UPDATE
                SET content = EXCLUDED.content,
                    message_count = EXCLUDED.message_count,
                    updated_at = NOW()
                RETURNING id, session_id, content, message_count, created_at, updated_at
                """,
                session_id, content, message_count
            )

            return MemorySummary(
                id=str(record['id']),
                session_id=str(record['session_id']),
                content=record['content'],
                message_count=record['message_count'],
                created_at=record['created_at'],
                updated_at=record['updated_at']
            )

    async def find_by_session_id(self, session_id: str) -> Optional[MemorySummary]:
        """根据会话 ID 查找记忆摘要"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                SELECT id, session_id, content, message_count, created_at, updated_at
                FROM memory_summaries
                WHERE session_id = $1
                """,
                session_id
            )

            if not record:
                return None

            return MemorySummary(
                id=str(record['id']),
                session_id=str(record['session_id']),
                content=record['content'],
                message_count=record['message_count'],
                created_at=record['created_at'],
                updated_at=record['updated_at']
            )

    async def update(
        self,
        session_id: str,
        content: str,
        message_count: int
    ) -> Optional[MemorySummary]:
        """更新记忆摘要"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                UPDATE memory_summaries
                SET content = $2, message_count = $3, updated_at = NOW()
                WHERE session_id = $1
                RETURNING id, session_id, content, message_count, created_at, updated_at
                """,
                session_id, content, message_count
            )

            if not record:
                return None

            return MemorySummary(
                id=str(record['id']),
                session_id=str(record['session_id']),
                content=record['content'],
                message_count=record['message_count'],
                created_at=record['created_at'],
                updated_at=record['updated_at']
            )


class MemorySegmentRepository:
    """记忆主题段仓储"""

    async def create(
        self,
        session_id: str,
        topic_name: str,
        start_message_id: str,
        end_message_id: str,
        summary_content: str,
        importance_score: float,
        message_count: int,
        total_importance: float,
        embedding: Optional[List[float]] = None
    ) -> MemorySegment:
        """创建记忆主题段"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            embedding_str = None
            if embedding:
                embedding_str = f"[{','.join(str(x) for x in embedding)}]"

            record = await conn.fetchrow(
                """
                INSERT INTO memory_segments (
                    session_id, topic_name, start_message_id, end_message_id,
                    summary_content, importance_score, message_count, total_importance, embedding
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::vector)
                RETURNING id, session_id, topic_name, start_message_id, end_message_id,
                          summary_content, importance_score, message_count, total_importance,
                          created_at, updated_at, embedding
                """,
                session_id, topic_name, start_message_id, end_message_id,
                summary_content, importance_score, message_count, total_importance, embedding_str
            )

            return MemorySegment(
                id=str(record['id']),
                session_id=str(record['session_id']),
                topic_name=record['topic_name'],
                start_message_id=str(record['start_message_id']),
                end_message_id=str(record['end_message_id']),
                summary_content=record['summary_content'],
                importance_score=record['importance_score'],
                message_count=record['message_count'],
                total_importance=record['total_importance'],
                created_at=record['created_at'],
                updated_at=record['updated_at'],
                embedding=record['embedding']
            )

    async def find_by_id(self, segment_id: str) -> Optional[MemorySegment]:
        """根据 ID 查找主题段"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                SELECT id, session_id, topic_name, start_message_id, end_message_id,
                       summary_content, importance_score, message_count, total_importance,
                       created_at, updated_at, embedding
                FROM memory_segments
                WHERE id = $1
                """,
                segment_id
            )

            if not record:
                return None

            return MemorySegment(
                id=str(record['id']),
                session_id=str(record['session_id']),
                topic_name=record['topic_name'],
                start_message_id=str(record['start_message_id']) if record['start_message_id'] else None,
                end_message_id=str(record['end_message_id']) if record['end_message_id'] else None,
                summary_content=record['summary_content'],
                importance_score=record['importance_score'],
                message_count=record['message_count'],
                total_importance=record['total_importance'],
                created_at=record['created_at'],
                updated_at=record['updated_at'],
                embedding=record['embedding']
            )

    async def find_by_session_id(self, session_id: str) -> List[MemorySegment]:
        """根据会话 ID 查找所有主题段"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            records = await conn.fetch(
                """
                SELECT id, session_id, topic_name, start_message_id, end_message_id,
                       summary_content, importance_score, message_count, total_importance,
                       created_at, updated_at, embedding
                FROM memory_segments
                WHERE session_id = $1
                ORDER BY created_at ASC
                """,
                session_id
            )

            return [
                MemorySegment(
                    id=str(record['id']),
                    session_id=str(record['session_id']),
                    topic_name=record['topic_name'],
                    start_message_id=str(record['start_message_id']) if record['start_message_id'] else None,
                    end_message_id=str(record['end_message_id']) if record['end_message_id'] else None,
                    summary_content=record['summary_content'],
                    importance_score=record['importance_score'],
                    message_count=record['message_count'],
                    total_importance=record['total_importance'],
                    created_at=record['created_at'],
                    updated_at=record['updated_at'],
                    embedding=record['embedding']
                )
                for record in records
            ]

    async def update(
        self,
        segment_id: str,
        topic_name: Optional[str] = None,
        summary_content: Optional[str] = None,
        importance_score: Optional[float] = None
    ) -> Optional[MemorySegment]:
        """更新主题段"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            updates = []
            params = [segment_id]
            param_idx = 2

            if topic_name is not None:
                updates.append(f"topic_name = ${param_idx}")
                params.append(topic_name)
                param_idx += 1

            if summary_content is not None:
                updates.append(f"summary_content = ${param_idx}")
                params.append(summary_content)
                param_idx += 1

            if importance_score is not None:
                updates.append(f"importance_score = ${param_idx}")
                params.append(importance_score)
                param_idx += 1

            if not updates:
                return await self.find_by_id(segment_id)

            query = f"""
                UPDATE memory_segments
                SET {', '.join(updates)}, updated_at = NOW()
                WHERE id = $1
                RETURNING id, session_id, topic_name, start_message_id, end_message_id,
                          summary_content, importance_score, message_count, total_importance,
                          created_at, updated_at, embedding
            """

            record = await conn.fetchrow(query, *params)

            if not record:
                return None

            return MemorySegment(
                id=str(record['id']),
                session_id=str(record['session_id']),
                topic_name=record['topic_name'],
                start_message_id=str(record['start_message_id']) if record['start_message_id'] else None,
                end_message_id=str(record['end_message_id']) if record['end_message_id'] else None,
                summary_content=record['summary_content'],
                importance_score=record['importance_score'],
                message_count=record['message_count'],
                total_importance=record['total_importance'],
                created_at=record['created_at'],
                updated_at=record['updated_at'],
                embedding=record['embedding']
            )

    async def delete(self, segment_id: str) -> bool:
        """删除主题段"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM memory_segments WHERE id = $1",
                segment_id
            )
            return "DELETE 1" in result

    async def find_by_importance_threshold(
        self,
        session_id: str,
        min_importance: float
    ) -> List[MemorySegment]:
        """根据重要性阈值查找主题段"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            records = await conn.fetch(
                """
                SELECT id, session_id, topic_name, start_message_id, end_message_id,
                       summary_content, importance_score, message_count, total_importance,
                       created_at, updated_at, embedding
                FROM memory_segments
                WHERE session_id = $1 AND importance_score >= $2
                ORDER BY importance_score DESC
                """,
                session_id, min_importance
            )

            return [
                MemorySegment(
                    id=str(record['id']),
                    session_id=str(record['session_id']),
                    topic_name=record['topic_name'],
                    start_message_id=str(record['start_message_id']) if record['start_message_id'] else None,
                    end_message_id=str(record['end_message_id']) if record['end_message_id'] else None,
                    summary_content=record['summary_content'],
                    importance_score=record['importance_score'],
                    message_count=record['message_count'],
                    total_importance=record['total_importance'],
                    created_at=record['created_at'],
                    updated_at=record['updated_at'],
                    embedding=record['embedding']
                )
                for record in records
            ]

    async def semantic_search(
        self,
        session_id: str,
        query_embedding: List[float],
        limit: int = 5
    ) -> List[MemorySegment]:
        """语义搜索 - 使用向量相似度查找主题段"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            embedding_str = f"[{','.join(str(x) for x in query_embedding)}]"

            records = await conn.fetch(
                """
                SELECT id, session_id, topic_name, start_message_id, end_message_id,
                       summary_content, importance_score, message_count, total_importance,
                       created_at, updated_at, embedding,
                       embedding <=> $2::vector as distance
                FROM memory_segments
                WHERE session_id = $1
                ORDER BY embedding <=> $2::vector
                LIMIT $3
                """,
                session_id, embedding_str, limit
            )

            return [
                MemorySegment(
                    id=str(record['id']),
                    session_id=str(record['session_id']),
                    topic_name=record['topic_name'],
                    start_message_id=str(record['start_message_id']) if record['start_message_id'] else None,
                    end_message_id=str(record['end_message_id']) if record['end_message_id'] else None,
                    summary_content=record['summary_content'],
                    importance_score=record['importance_score'],
                    message_count=record['message_count'],
                    total_importance=record['total_importance'],
                    created_at=record['created_at'],
                    updated_at=record['updated_at'],
                    embedding=record['embedding']
                )
                for record in records
            ]


class ImportanceScoreRepository:
    """重要性分数仓储 - 管理消息重要性评分和向量嵌入"""

    async def update_score(
        self,
        message_id: str,
        importance_score: float,
        topic_tag: Optional[str] = None
    ) -> bool:
        """更新消息重要性分数和可选的主题标签"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            if topic_tag is not None:
                result = await conn.execute(
                    """
                    UPDATE messages
                    SET importance_score = $2, topic_tag = $3
                    WHERE id = $1
                    """,
                    message_id, importance_score, topic_tag
                )
            else:
                result = await conn.execute(
                    """
                    UPDATE messages
                    SET importance_score = $2
                    WHERE id = $1
                    """,
                    message_id, importance_score
                )
            return "UPDATE 1" in result

    async def get_score(self, message_id: str) -> float:
        """获取消息重要性分数（默认 0.5）"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            score = await conn.fetchval(
                """
                SELECT importance_score
                FROM messages
                WHERE id = $1
                """,
                message_id
            )
            return score if score is not None else 0.5

    async def get_score_and_topic(self, message_id: str) -> tuple:
        """获取消息重要性分数和主题标签"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                SELECT importance_score, topic_tag
                FROM messages
                WHERE id = $1
                """,
                message_id
            )
            if not record:
                return 0.5, None
            return record['importance_score'] or 0.5, record['topic_tag']

    async def batch_update_scores(
        self,
        updates: list[tuple[str, float]]
    ) -> int:
        """批量更新消息重要性分数"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.executemany(
                """
                UPDATE messages
                SET importance_score = $2
                WHERE id = $1
                """,
                updates
            )
            return len(updates)

    async def get_messages_by_importance_threshold(
        self,
        session_id: str,
        min_importance: float,
        limit: int = 100
    ) -> list[tuple[str, float, str]]:
        """获取重要性超过阈值的消息"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            records = await conn.fetch(
                """
                SELECT id, importance_score, content
                FROM messages
                WHERE session_id = $1 AND importance_score >= $2
                ORDER BY importance_score DESC
                LIMIT $3
                """,
                session_id, min_importance, limit
            )
            return [
                (str(record['id']), record['importance_score'], record['content'])
                for record in records
            ]

    async def batch_update_topic_tags(
        self,
        message_ids: list[str],
        topic_tag: str
    ) -> int:
        """批量更新消息的 topic_tag"""
        if not message_ids:
            return 0

        pool = await get_pool()
        async with pool.acquire() as conn:
            # 使用 unnest 批量更新
            result = await conn.execute(
                """
                UPDATE messages
                SET topic_tag = $1
                WHERE id = ANY($2)
                """,
                topic_tag, message_ids
            )
            return int(result.split()[-1]) if "UPDATE" in result else 0

    async def update_embedding(
        self,
        message_id: str,
        embedding: list[float]
    ) -> bool:
        """更新消息向量嵌入"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            embedding_str = f"[{','.join(str(x) for x in embedding)}]"

            result = await conn.execute(
                """
                UPDATE messages
                SET embedding = $2::vector
                WHERE id = $1
                """,
                message_id, embedding_str
            )
            return "UPDATE 1" in result

    async def get_messages_without_embedding(
        self,
        session_id: str,
        limit: int = 100
    ) -> list[dict]:
        """获取没有向量嵌入的消息"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            records = await conn.fetch(
                """
                SELECT id, role, content, created_at
                FROM messages
                WHERE session_id = $1 AND embedding IS NULL
                ORDER BY created_at ASC
                LIMIT $2
                """,
                session_id, limit
            )
            return [
                {
                    'id': str(record['id']),
                    'role': record['role'],
                    'content': record['content'],
                    'created_at': record['created_at']
                }
                for record in records
            ]
