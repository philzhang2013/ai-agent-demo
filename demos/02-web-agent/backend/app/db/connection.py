"""
数据库连接管理
"""
import asyncio
from typing import AsyncIterator
import asyncpg
from asyncpg import Connection, Pool

from app.config import get_settings

settings = get_settings()

# 全局连接池
_pool: Pool | None = None


class AsyncConnectionContext:
    """异步连接上下文管理器"""

    def __init__(self, pool: Pool):
        self._pool = pool
        self._connection: Connection | None = None

    async def __aenter__(self) -> Connection:
        self._connection = await self._pool.acquire()
        return self._connection

    async def __aexit__(self, *args):
        if self._connection:
            await self._pool.release(self._connection)


async def get_pool() -> Pool:
    """获取连接池"""
    global _pool

    if _pool is None:
        _pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=2,
            max_size=10,
            command_timeout=60
        )

    return _pool


async def get_connection() -> AsyncIterator[Connection]:
    """获取数据库连接（上下文管理器）"""
    pool = await get_pool()
    async with pool.acquire() as connection:
        yield connection


def get_connection_context() -> AsyncConnectionContext:
    """获取数据库连接上下文（用于仓储）"""
    # 这个函数需要在异步上下文中调用
    # 为了简化，我们在仓储中直接使用 pool.acquire()
    return _get_connection_context_sync()


async def _get_connection_context_async() -> AsyncConnectionContext:
    """异步版本的连接上下文获取"""
    pool = await get_pool()
    return AsyncConnectionContext(pool)


def _get_connection_context_sync() -> AsyncConnectionContext:
    """同步版本的连接上下文获取（实际上返回包装对象）"""
    # 这是一个简化的实现，实际使用时需要在异步上下文中
    class DelayedAsyncContext:
        def __init__(self):
            self._ctx: AsyncConnectionContext | None = None

        async def _init(self):
            self._ctx = await _get_connection_context_async()
            return self._ctx

        async def __aenter__(self):
            self._ctx = await _get_connection_context_async()
            return await self._ctx.__aenter__()

        async def __aexit__(self, *args):
            if self._ctx:
                await self._ctx.__aexit__(*args)

    return DelayedAsyncContext()  # type: ignore


async def close_pool():
    """关闭连接池"""
    global _pool

    if _pool:
        await _pool.close()
        _pool = None
