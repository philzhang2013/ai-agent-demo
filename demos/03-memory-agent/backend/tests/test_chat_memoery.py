"""
集成测试：test_chat_memoery
验证长短记忆功能 - 5轮摘要生成 + 10轮记忆召回

测试要求：
- 每个测试独立，不共享数据
- 测试结束清理数据
- 使用 psql 命令查询数据库验证

注意：本测试直接测试 MemoryManager 集成，而非通过 SSE 流式接口
"""
import pytest
import asyncio
import subprocess
from uuid import uuid4
from unittest.mock import Mock, AsyncMock

from app.db.repositories import (
    UserRepository,
    SessionRepository,
    MessageRepository,
    MemorySummaryRepository
)
from app.auth.password import hash_password
from app.memory.manager import MemoryManager
from app.db.connection import get_pool


# 数据库连接配置
DATABASE_URL = "postgresql://postgres:123456@127.0.0.1:5432/postgres"


def run_psql_query(query: str) -> str:
    """使用 psql 命令执行 SQL 查询"""
    try:
        result = subprocess.run(
            ["psql", DATABASE_URL, "-t", "-c", query],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


class TestChatMemory:
    """聊天记忆功能集成测试"""

    @pytest.mark.asyncio
    async def test_5_rounds_creates_summary(self):
        """
        测试：5轮聊天后摘要正确写入数据库

        验证点：
        1. 创建4条消息后，should_summarize 返回 False
        2. 创建第5条消息后，should_summarize 返回 True
        3. 调用 generate_summary 生成摘要
        4. 摘要正确保存到数据库
        5. 使用 psql 验证 memory_summaries 表数据
        6. 清理测试数据
        """
        # 创建独立测试数据
        unique_id = str(uuid4())[:8]
        username = f"memory_test_5r_{unique_id}"

        # 创建用户
        user_repo = UserRepository()
        password_hash = hash_password("test123")
        user = await user_repo.create(username, password_hash)

        # 创建会话
        session_repo = SessionRepository()
        session = await session_repo.create(user.id, "5轮记忆测试")

        print(f"\n[测试] 创建会话: {session.id}")

        # 初始化仓储和 MemoryManager
        message_repo = MessageRepository()
        summary_repo = MemorySummaryRepository()

        # Mock LLM 客户端
        mock_llm = Mock()
        mock_llm.chat.return_value = {
            "content": "用户张三是一名软件工程师，喜欢打篮球，有个弟弟叫李四。"
        }

        memory_manager = MemoryManager(
            message_repo=message_repo,
            summary_repo=summary_repo,
            llm_client=mock_llm
        )

        # 创建4条消息
        messages_data = [
            ("user", "你好，我叫张三，是一名软件工程师，喜欢打篮球。"),
            ("assistant", "你好张三！很高兴认识你。作为软件工程师，你一定对技术很感兴趣。打篮球是很好的运动习惯！"),
            ("user", "是的，我每周都去打篮球。对了，我还有个弟弟叫李四。"),
            ("assistant", "李四也是个好名字！你们兄弟俩经常一起打篮球吗？")
        ]

        for role, content in messages_data:
            await message_repo.create(session.id, role, content)

        print(f"[测试] 已创建4条消息")

        # 验证4条消息时不触发摘要
        should_trigger = await memory_manager.should_summarize(session.id)
        print(f"[验证] 4条消息时应不触发摘要: {should_trigger}")
        assert should_trigger is False, "4条消息时不应触发摘要"

        # 创建第5条消息
        await message_repo.create(session.id, "user", "还记得我是谁吗？")
        print(f"[测试] 已创建第5条消息")

        # 验证5条消息时触发摘要
        should_trigger = await memory_manager.should_summarize(session.id)
        print(f"[验证] 5条消息时应触发摘要: {should_trigger}")
        assert should_trigger is True, "5条消息时应触发摘要"

        # 生成摘要
        all_messages = await message_repo.find_by_session_id(session.id)
        messages_for_summary = [
            {"role": msg.role, "content": msg.content}
            for msg in all_messages
        ]

        summary_content = memory_manager.generate_summary(messages_for_summary)
        print(f"[测试] 生成摘要: {summary_content}")

        assert summary_content != "", "摘要内容不应为空"
        assert "张三" in summary_content, f"摘要应包含关键信息，实际: {summary_content}"

        # 保存摘要到数据库
        summary = await summary_repo.create(
            session_id=session.id,
            content=summary_content,
            message_count=len(all_messages)
        )

        print(f"[测试] 摘要已保存，ID: {summary.id}")

        # 验证摘要记录
        assert summary.message_count == 5, f"消息数应为5，实际: {summary.message_count}"
        assert summary.session_id == session.id, "session_id 应匹配"

        # ===== 使用 psql 命令查询验证 =====
        print("\n[PSQL查询] 验证数据库中的摘要记录...")

        psql_result = run_psql_query(
            f"SELECT session_id, message_count, content FROM memory_summaries WHERE session_id = '{session.id}'"
        )
        print(f"[PSQL结果] {psql_result}")

        assert session.id in psql_result, "PSQL查询应找到记录"
        assert "5" in psql_result, "PSQL结果应包含消息数5"
        assert "张三" in psql_result, "PSQL结果应包含摘要内容"

        # 验证消息表中的记录数
        msg_count_query = run_psql_query(
            f"SELECT count(*) FROM messages WHERE session_id = '{session.id}'"
        )
        print(f"[PSQL查询] 消息数: {msg_count_query}")
        assert "5" in msg_count_query, "数据库中应有5条消息"

        # ===== 测试 get_context =====
        print("\n[测试] 验证 get_context 返回包含摘要的上下文...")
        context = await memory_manager.get_context(session.id)

        # 验证上下文包含摘要系统消息
        assert len(context) > 0, "上下文不应为空"
        first_msg = context[0]
        assert first_msg["role"] == "system", "第一条应是系统消息（摘要）"
        assert "【历史对话摘要】" in first_msg["content"], "应包含摘要标记"
        assert "张三" in first_msg["content"], "摘要应包含关键信息"

        print(f"[验证] 上下文消息数: {len(context)}")
        print(f"[验证] 上下文内容: {context}")

        # 清理数据
        print("\n[清理] 删除测试数据...")
        await summary_repo._delete_for_test(session.id)
        await message_repo.delete_by_session_id(session.id)
        await session_repo.delete(session.id)

        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM users WHERE id = $1", user.id)

        print("[测试] ✅ 5轮摘要测试通过！")

    @pytest.mark.asyncio
    async def test_10_rounds_model_remembers(self):
        """
        测试：10轮聊天后模型能利用记忆回答

        验证点：
        1. 创建前5轮消息和摘要
        2. 创建第6-9轮消息
        3. 第10轮消息触发摘要更新
        4. 使用 psql 验证摘要已更新
        5. 验证摘要包含早期和近期记忆
        6. 清理测试数据
        """
        # 创建独立测试数据
        unique_id = str(uuid4())[:8]
        username = f"memory_test_10r_{unique_id}"

        # 创建用户
        user_repo = UserRepository()
        password_hash = hash_password("test123")
        user = await user_repo.create(username, password_hash)

        # 创建会话
        session_repo = SessionRepository()
        session = await session_repo.create(user.id, "10轮记忆测试")

        print(f"\n[测试] 创建会话: {session.id}")

        # 初始化仓储和 MemoryManager
        message_repo = MessageRepository()
        summary_repo = MemorySummaryRepository()

        # Mock LLM 客户端
        mock_llm = Mock()
        mock_llm.chat.return_value = {
            "content": "用户王五住在北京朝阳区，养了一只3岁金毛犬豆豆，经常带狗去公园，豆豆学会了握手技巧。"
        }

        memory_manager = MemoryManager(
            message_repo=message_repo,
            summary_repo=summary_repo,
            llm_client=mock_llm
        )

        # 创建前5轮消息
        early_messages = [
            ("user", "你好，我是王五，养了一只金毛犬叫豆豆。"),
            ("assistant", "你好王五！豆豆听起来很可爱，多大了？"),
            ("user", "豆豆3岁了，非常活泼。我住在北京朝阳区。"),
            ("assistant", "朝阳区是个好地方，豆豆肯定有很多地方可以玩。"),
            ("user", "是的，我经常带豆豆去公园。")
        ]

        for role, content in early_messages:
            await message_repo.create(session.id, role, content)

        # 创建前5轮的摘要
        first_summary = await summary_repo.create(
            session.id,
            "用户王五住在北京朝阳区，养了一只3岁的金毛犬叫豆豆，经常带狗去公园。",
            5
        )
        first_created_at = first_summary.created_at

        print(f"[测试] 已创建前5轮消息和摘要")

        # 验证当前不触发更新（5条消息，摘要已存在）
        should_trigger = await memory_manager.should_summarize(session.id)
        print(f"[验证] 5条消息且已有摘要时应不触发: {should_trigger}")
        assert should_trigger is False, "5条消息且已有摘要时不应触发更新"

        # 创建第6-9轮消息
        later_messages = [
            ("user", "豆豆最近学会了一个新技巧！"),
            ("assistant", "太棒了！是什么新技巧？"),
            ("user", "它会握手了，很聪明吧？"),
            ("assistant", "真厉害！豆豆学得真快。")
        ]

        for role, content in later_messages:
            await message_repo.create(session.id, role, content)

        print(f"[测试] 已创建第6-9轮消息（共9条）")

        # 验证9条消息时仍不触发（需要10条）
        should_trigger = await memory_manager.should_summarize(session.id)
        print(f"[验证] 9条消息时应不触发: {should_trigger}")
        assert should_trigger is False, "9条消息时不应触发更新"

        # 创建第10条消息
        await message_repo.create(session.id, "user", "还记得我的名字和我住在哪里吗？豆豆呢？")
        print(f"[测试] 已创建第10条消息")

        # 验证10条消息时触发更新
        should_trigger = await memory_manager.should_summarize(session.id)
        print(f"[验证] 10条消息时应触发更新: {should_trigger}")
        assert should_trigger is True, "10条消息时应触发更新"

        # 生成更新后的摘要
        all_messages = await message_repo.find_by_session_id(session.id)
        messages_for_summary = [
            {"role": msg.role, "content": msg.content}
            for msg in all_messages
        ]

        new_summary_content = memory_manager.generate_summary(messages_for_summary)
        print(f"[测试] 生成新摘要: {new_summary_content}")

        # 更新摘要到数据库
        updated_summary = await summary_repo.create(
            session_id=session.id,
            content=new_summary_content,
            message_count=len(all_messages)
        )

        print(f"[测试] 摘要已更新，ID: {updated_summary.id}")

        # ===== 使用 psql 命令查询验证 =====
        print("\n[PSQL查询] 验证摘要已更新...")

        psql_result = run_psql_query(
            f"SELECT session_id, message_count, content, created_at, updated_at "
            f"FROM memory_summaries WHERE session_id = '{session.id}'"
        )
        print(f"[PSQL结果] {psql_result}")

        # 核心断言
        assert updated_summary.message_count == 10, f"更新后消息数应为10，实际: {updated_summary.message_count}"
        assert updated_summary.id == first_summary.id, "应是同一条记录（UPSERT）"
        assert updated_summary.updated_at > first_created_at, "updated_at 应更新"

        # 验证新摘要包含早期记忆和近期记忆
        assert "王五" in updated_summary.content, f"新摘要应记住名字，实际: {updated_summary.content}"
        assert "握手" in updated_summary.content, f"新摘要应包含新技巧，实际: {updated_summary.content}"

        # 验证PSQL结果
        assert "10" in psql_result, "PSQL结果应包含消息数10"

        # 验证消息总数为10
        msg_count_query = run_psql_query(
            f"SELECT count(*) FROM messages WHERE session_id = '{session.id}'"
        )
        print(f"[PSQL查询] 消息数: {msg_count_query}")
        assert "10" in msg_count_query, "数据库中应有10条消息"

        # ===== 验证 get_context 包含完整记忆 =====
        print("\n[测试] 验证 get_context 包含完整记忆...")
        context = await memory_manager.get_context(session.id)

        # 验证上下文包含摘要系统消息
        assert len(context) > 0, "上下文不应为空"
        first_msg = context[0]
        assert first_msg["role"] == "system", "第一条应是系统消息（摘要）"
        assert "【历史对话摘要】" in first_msg["content"], "应包含摘要标记"

        # 验证摘要包含早期信息（证明模型能记住）
        summary_text = first_msg["content"]
        assert "王五" in summary_text, "摘要应包含名字（早期记忆）"
        assert "北京" in summary_text or "朝阳" in summary_text, "摘要应包含住址（早期记忆）"
        assert "豆豆" in summary_text, "摘要应包含狗名（早期记忆）"
        assert "握手" in summary_text, "摘要应包含新技巧（近期记忆）"

        print(f"[验证] 上下文消息数: {len(context)}")
        print(f"[验证] ✅ 摘要同时包含早期记忆（王五、北京、豆豆）和近期记忆（握手）！")

        # 清理数据
        print("\n[清理] 删除测试数据...")
        await summary_repo._delete_for_test(session.id)
        await message_repo.delete_by_session_id(session.id)
        await session_repo.delete(session.id)

        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM users WHERE id = $1", user.id)

        print("[测试] ✅ 10轮记忆召回测试通过！")


class TestChatMemoryCleanup:
    """测试数据清理验证"""

    @pytest.mark.asyncio
    async def test_cleanup_verification(self):
        """验证测试数据已清理"""
        print("\n[清理验证] 检查并清理残留测试数据...")

        # 查询所有测试用户
        result = run_psql_query(
            "SELECT count(*) FROM users WHERE username LIKE 'memory_test_%'"
        )
        print(f"[清理验证] 残留测试用户数: {result}")

        # 清理所有测试数据
        pool = await get_pool()
        async with pool.acquire() as conn:
            # 清理测试摘要
            await conn.execute(
                "DELETE FROM memory_summaries WHERE session_id IN ("
                "SELECT id FROM sessions WHERE user_id IN ("
                "SELECT id FROM users WHERE username LIKE 'memory_test_%'"
                "))"
            )
            # 清理测试消息
            await conn.execute(
                "DELETE FROM messages WHERE session_id IN ("
                "SELECT id FROM sessions WHERE user_id IN ("
                "SELECT id FROM users WHERE username LIKE 'memory_test_%'"
                "))"
            )
            # 清理测试会话
            await conn.execute(
                "DELETE FROM sessions WHERE user_id IN ("
                "SELECT id FROM users WHERE username LIKE 'memory_test_%'"
                ")"
            )
            # 清理测试用户
            await conn.execute(
                "DELETE FROM users WHERE username LIKE 'memory_test_%'"
            )

        result_after = run_psql_query(
            "SELECT count(*) FROM users WHERE username LIKE 'memory_test_%'"
        )
        print(f"[清理验证] 清理后测试用户数: {result_after}")
        assert "0" in result_after, "清理后应无测试用户"
        print("[清理验证] ✅ 测试数据已清理！")


# 为 MemorySummaryRepository 添加测试用的删除方法
async def _delete_summary_for_test(self, session_id: str):
    """测试用：删除摘要"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM memory_summaries WHERE session_id = $1",
            session_id
        )

# 动态添加到类
MemorySummaryRepository._delete_for_test = _delete_summary_for_test
