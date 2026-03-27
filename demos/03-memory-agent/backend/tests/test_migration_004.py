"""
测试 004_add_smart_memory 迁移
验证表结构和字段正确创建
"""
import pytest
from app.db.connection import get_pool


class TestSmartMemoryMigration:
    """测试智能记忆相关数据库迁移"""

    @pytest.mark.asyncio
    async def test_pgvector_extension_exists(self):
        """测试 pgvector 扩展已启用"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM pg_extension WHERE extname = 'vector'"
            )
            assert row is not None, "pgvector 扩展未启用"

    @pytest.mark.asyncio
    async def test_messages_table_has_importance_score(self):
        """测试 messages 表有 importance_score 字段"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'messages' AND column_name = 'importance_score'
                """
            )
            assert row is not None, "messages 表缺少 importance_score 字段"
            assert row['data_type'] == 'double precision', "importance_score 类型应为 FLOAT"

    @pytest.mark.asyncio
    async def test_messages_table_has_topic_tag(self):
        """测试 messages 表有 topic_tag 字段"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = 'messages' AND column_name = 'topic_tag'
                """
            )
            assert row is not None, "messages 表缺少 topic_tag 字段"
            assert row['data_type'] == 'character varying', "topic_tag 类型应为 VARCHAR"

    @pytest.mark.asyncio
    async def test_messages_table_has_embedding(self):
        """测试 messages 表有 embedding 字段（pgvector）"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT column_name, data_type, udt_name
                FROM information_schema.columns
                WHERE table_name = 'messages' AND column_name = 'embedding'
                """
            )
            assert row is not None, "messages 表缺少 embedding 字段"
            # pgvector 的 vector 类型在 udt_name 中显示
            assert 'vector' in row['udt_name'].lower(), "embedding 类型应为 VECTOR"

    @pytest.mark.asyncio
    async def test_memory_segments_table_exists(self):
        """测试 memory_segments 表已创建"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_name = 'memory_segments'
                """
            )
            assert row is not None, "memory_segments 表不存在"

    @pytest.mark.asyncio
    async def test_memory_segments_has_required_columns(self):
        """测试 memory_segments 表有所有必需字段"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'memory_segments'
                ORDER BY ordinal_position
                """
            )
            columns = [r['column_name'] for r in rows]

            required_columns = [
                'id', 'session_id', 'topic_name',
                'start_message_id', 'end_message_id',
                'summary_content', 'importance_score', 'embedding',
                'message_count', 'total_importance',
                'created_at', 'updated_at'
            ]

            for col in required_columns:
                assert col in columns, f"memory_segments 表缺少字段: {col}"

    @pytest.mark.asyncio
    async def test_messages_embedding_index_exists(self):
        """测试 messages 表向量索引已创建"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'messages' AND indexname = 'idx_messages_embedding'
                """
            )
            assert row is not None, "idx_messages_embedding 索引不存在"
            assert 'ivfflat' in row['indexdef'].lower(), "应使用 ivfflat 索引"

    @pytest.mark.asyncio
    async def test_segments_embedding_index_exists(self):
        """测试 memory_segments 表向量索引已创建"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'memory_segments' AND indexname = 'idx_segments_embedding'
                """
            )
            assert row is not None, "idx_segments_embedding 索引不存在"
            assert 'ivfflat' in row['indexdef'].lower(), "应使用 ivfflat 索引"

    @pytest.mark.asyncio
    async def test_messages_importance_index_exists(self):
        """测试 messages 表 importance_score 索引已创建"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = 'messages' AND indexname = 'idx_messages_importance'
                """
            )
            assert row is not None, "idx_messages_importance 索引不存在"
