"""
数据库查询脚本 - 验证数据存储
"""
import asyncio
import asyncpg
import sys

# 数据库连接字符串
DATABASE_URL = "postgresql://postgres:123456@127.0.0.1:5432/postgres"


async def check_database():
    """检查数据库连接和数据存储情况"""
    try:
        # 连接数据库
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ 数据库连接成功\n")

        # 1. 检查表是否存在
        tables_query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
        tables = await conn.fetch(tables_query)
        print("📋 数据库表列表:")
        for table in tables:
            print(f"   - {table['table_name']}")
        print()

        # 2. 查询 users 表
        print("👤 Users 表:")
        user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        print(f"   用户数: {user_count}")
        if user_count > 0:
            users = await conn.fetch("SELECT id, username, created_at FROM users LIMIT 5")
            for user in users:
                print(f"   - {user['username']} (ID: {user['id'][:8]}...)")
        print()

        # 3. 查询 sessions 表
        print("💬 Sessions 表:")
        session_count = await conn.fetchval("SELECT COUNT(*) FROM sessions")
        print(f"   会话数: {session_count}")
        if session_count > 0:
            sessions = await conn.fetch("""
                SELECT s.id, s.title, u.username, s.created_at, s.updated_at
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                ORDER BY s.updated_at DESC
                LIMIT 5
            """)
            for session in sessions:
                print(f"   - {session['title']} (用户: {session['username']})")
        print()

        # 4. 查询 messages 表
        print("📝 Messages 表:")
        message_count = await conn.fetchval("SELECT COUNT(*) FROM messages")
        print(f"   消息总数: {message_count}")
        if message_count > 0:
            messages = await conn.fetch("""
                SELECT m.id, m.role, LEFT(m.content, 50) as preview, m.created_at
                FROM messages m
                ORDER BY m.created_at DESC
                LIMIT 5
            """)
            for msg in messages:
                preview = msg['preview'] + "..." if len(msg['preview']) == 50 else msg['preview']
                print(f"   [{msg['role']}] {preview}")
        print()

        # 5. 统计信息
        print("📊 统计信息:")
        stats = await conn.fetch("""
            SELECT
                s.id as session_id,
                s.title,
                COUNT(m.id) as message_count
            FROM sessions s
            LEFT JOIN messages m ON s.id = m.session_id
            GROUP BY s.id, s.title
            ORDER BY message_count DESC
            LIMIT 5
        """)
        for stat in stats:
            print(f"   - {stat['title']}: {stat['message_count']} 条消息")

        await conn.close()
        print("\n✅ 查询完成")

    except asyncpg.exceptions.PostgresError as e:
        print(f"❌ PostgreSQL 错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(check_database())
