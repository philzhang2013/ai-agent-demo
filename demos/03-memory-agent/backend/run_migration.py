"""
数据库迁移脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.connection import get_pool, close_pool


async def run_migration():
    """运行数据库迁移"""

    # 读取 SQL 文件
    with open('migrations/001_initial_schema.sql', 'r') as f:
        sql = f.read()

    # 连接数据库
    pool = await get_pool()

    async with pool.acquire() as conn:
        # 执行 SQL
        await conn.execute(sql)

    print("✅ 数据库迁移完成！")

    # 关闭连接
    await close_pool()


if __name__ == '__main__':
    asyncio.run(run_migration())
