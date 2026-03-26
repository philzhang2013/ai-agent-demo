"""
MemoryManager 测试
严格遵循TDD：先写测试，确保测试失败（RED状态）
"""
import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import Mock, AsyncMock, MagicMock

from app.db.repositories import (
    UserRepository,
    SessionRepository,
    MessageRepository,
    MemorySummaryRepository,
    MemorySummary
)
from app.auth.password import hash_password


class TestMemoryManager:
    """测试 MemoryManager 核心逻辑"""

    @pytest.mark.asyncio
    async def test_should_summarize_true_at_5_messages(self):
        """5条消息触发首次摘要"""
        # Arrange
        user_repo = UserRepository()
        session_repo = SessionRepository()
        message_repo = MessageRepository()

        password_hash = hash_password("password123")
        unique_id = str(uuid4())[:8]
        user = await user_repo.create(f"testuser_mm_5_{unique_id}", password_hash)
        session = await session_repo.create(user.id)

        # 创建5条消息
        for i in range(5):
            await message_repo.create(session.id, "user", f"消息{i+1}")

        # 创建 mock 的 summary_repo（返回None表示没有摘要）
        summary_repo = Mock()
        summary_repo.find_by_session_id = AsyncMock(return_value=None)

        # 创建 MemoryManager
        from app.memory.manager import MemoryManager
        manager = MemoryManager(message_repo, summary_repo, Mock())

        # Act
        result = await manager.should_summarize(session.id)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_should_summarize_true_at_10_messages_with_old_summary(self):
        """10条消息触发更新（已有5条消息的摘要）"""
        # Arrange
        user_repo = UserRepository()
        session_repo = SessionRepository()
        message_repo = MessageRepository()
        summary_repo = MemorySummaryRepository()

        password_hash = hash_password("password123")
        unique_id = str(uuid4())[:8]
        user = await user_repo.create(f"testuser_mm_10_{unique_id}", password_hash)
        session = await session_repo.create(user.id)

        # 创建10条消息
        for i in range(10):
            await message_repo.create(session.id, "user", f"消息{i+1}")

        # 创建5条消息的摘要
        await summary_repo.create(session.id, "前5条摘要", 5)

        # 创建 MemoryManager
        from app.memory.manager import MemoryManager
        manager = MemoryManager(message_repo, summary_repo, Mock())

        # Act
        result = await manager.should_summarize(session.id)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_should_summarize_true_at_15_messages(self):
        """15条消息再次更新（已有10条消息的摘要）"""
        # Arrange
        user_repo = UserRepository()
        session_repo = SessionRepository()
        message_repo = MessageRepository()
        summary_repo = MemorySummaryRepository()

        password_hash = hash_password("password123")
        unique_id = str(uuid4())[:8]
        user = await user_repo.create(f"testuser_mm_15_{unique_id}", password_hash)
        session = await session_repo.create(user.id)

        # 创建15条消息
        for i in range(15):
            await message_repo.create(session.id, "user", f"消息{i+1}")

        # 创建10条消息的摘要
        await summary_repo.create(session.id, "前10条摘要", 10)

        # 创建 MemoryManager
        from app.memory.manager import MemoryManager
        manager = MemoryManager(message_repo, summary_repo, Mock())

        # Act
        result = await manager.should_summarize(session.id)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_should_summarize_false_at_4_messages(self):
        """4条消息不触发摘要"""
        # Arrange
        user_repo = UserRepository()
        session_repo = SessionRepository()
        message_repo = MessageRepository()

        password_hash = hash_password("password123")
        unique_id = str(uuid4())[:8]
        user = await user_repo.create(f"testuser_mm_4_{unique_id}", password_hash)
        session = await session_repo.create(user.id)

        # 创建4条消息
        for i in range(4):
            await message_repo.create(session.id, "user", f"消息{i+1}")

        summary_repo = Mock()
        summary_repo.find_by_session_id = AsyncMock(return_value=None)

        from app.memory.manager import MemoryManager
        manager = MemoryManager(message_repo, summary_repo, Mock())

        # Act
        result = await manager.should_summarize(session.id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_should_summarize_false_at_6_to_9_messages(self):
        """6-9条不触发（在更新间隔内，已有5条摘要）"""
        # Arrange
        user_repo = UserRepository()
        session_repo = SessionRepository()
        message_repo = MessageRepository()
        summary_repo = MemorySummaryRepository()

        password_hash = hash_password("password123")
        unique_id = str(uuid4())[:8]
        user = await user_repo.create(f"testuser_mm_7_{unique_id}", password_hash)
        session = await session_repo.create(user.id)

        # 创建7条消息
        for i in range(7):
            await message_repo.create(session.id, "user", f"消息{i+1}")

        # 创建5条消息的摘要
        await summary_repo.create(session.id, "前5条摘要", 5)

        from app.memory.manager import MemoryManager
        manager = MemoryManager(message_repo, summary_repo, Mock())

        # Act
        result = await manager.should_summarize(session.id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_should_summarize_false_at_11_to_14_messages(self):
        """11-14条不触发（在第二次更新间隔内，已有10条摘要）"""
        # Arrange
        user_repo = UserRepository()
        session_repo = SessionRepository()
        message_repo = MessageRepository()
        summary_repo = MemorySummaryRepository()

        password_hash = hash_password("password123")
        unique_id = str(uuid4())[:8]
        user = await user_repo.create(f"testuser_mm_12_{unique_id}", password_hash)
        session = await session_repo.create(user.id)

        # 创建12条消息
        for i in range(12):
            await message_repo.create(session.id, "user", f"消息{i+1}")

        # 创建10条消息的摘要
        await summary_repo.create(session.id, "前10条摘要", 10)

        from app.memory.manager import MemoryManager
        manager = MemoryManager(message_repo, summary_repo, Mock())

        # Act
        result = await manager.should_summarize(session.id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_generate_summary_success(self):
        """正常生成摘要"""
        # Arrange
        from app.providers.base import ChatResponse

        mock_llm = Mock()
        mock_llm.chat = AsyncMock(return_value=ChatResponse(content="这是生成的摘要"))

        from app.memory.manager import MemoryManager
        manager = MemoryManager(Mock(), Mock(), mock_llm, model="glm-5")

        messages = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！有什么可以帮助你？"},
        ]

        # Act
        summary = await manager.generate_summary(messages)

        # Assert
        assert summary == "这是生成的摘要"
        mock_llm.chat.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_summary_handles_error(self):
        """LLM错误处理"""
        # Arrange
        mock_llm = Mock()
        mock_llm.chat = AsyncMock(side_effect=Exception("LLM服务错误"))

        from app.memory.manager import MemoryManager
        manager = MemoryManager(Mock(), Mock(), mock_llm, model="glm-5")

        messages = [{"role": "user", "content": "测试"}]

        # Act
        summary = await manager.generate_summary(messages)

        # Assert
        assert summary == ""  # 错误时返回空字符串

    @pytest.mark.asyncio
    async def test_get_context_with_summary(self):
        """有摘要时获取上下文 - 返回摘要 + 最近3条消息"""
        # Arrange
        user_repo = UserRepository()
        session_repo = SessionRepository()
        message_repo = MessageRepository()
        summary_repo = MemorySummaryRepository()

        password_hash = hash_password("password123")
        unique_id = str(uuid4())[:8]
        user = await user_repo.create(f"testuser_ctx_{unique_id}", password_hash)
        session = await session_repo.create(user.id)

        # 创建10条消息
        for i in range(10):
            await message_repo.create(session.id, "user" if i % 2 == 0 else "assistant", f"消息{i+1}")

        # 创建摘要
        await summary_repo.create(session.id, "会话摘要内容", 10)

        from app.memory.manager import MemoryManager
        manager = MemoryManager(message_repo, summary_repo, Mock())

        # Act
        context = await manager.get_context(session.id)

        # Assert
        assert len(context) == 4  # 1条摘要 + 3条消息
        assert context[0]["role"] == "system"
        assert "会话摘要内容" in context[0]["content"]
        # 后3条是最近的消息
        assert context[1]["role"] in ["user", "assistant"]
        assert context[2]["role"] in ["user", "assistant"]
        assert context[3]["role"] in ["user", "assistant"]

    @pytest.mark.asyncio
    async def test_get_context_without_summary(self):
        """无摘要时获取上下文 - 返回最近5条消息"""
        # Arrange
        user_repo = UserRepository()
        session_repo = SessionRepository()
        message_repo = MessageRepository()
        summary_repo = MemorySummaryRepository()

        password_hash = hash_password("password123")
        unique_id = str(uuid4())[:8]
        user = await user_repo.create(f"testuser_nosum_{unique_id}", password_hash)
        session = await session_repo.create(user.id)

        # 创建8条消息
        for i in range(8):
            await message_repo.create(session.id, "user" if i % 2 == 0 else "assistant", f"消息{i+1}")

        # 不创建摘要

        from app.memory.manager import MemoryManager
        manager = MemoryManager(message_repo, summary_repo, Mock())

        # Act
        context = await manager.get_context(session.id)

        # Assert
        assert len(context) == 5  # 最近5条消息
        # 所有消息都是原始消息，没有系统摘要
        for msg in context:
            assert msg["role"] in ["user", "assistant"]

    @pytest.mark.asyncio
    async def test_get_context_returns_last_3_messages_with_summary(self):
        """验证有摘要时返回最近3条消息"""
        # Arrange
        user_repo = UserRepository()
        session_repo = SessionRepository()
        message_repo = MessageRepository()
        summary_repo = MemorySummaryRepository()

        password_hash = hash_password("password123")
        unique_id = str(uuid4())[:8]
        user = await user_repo.create(f"testuser_last3_{unique_id}", password_hash)
        session = await session_repo.create(user.id)

        # 创建12条消息
        for i in range(12):
            await message_repo.create(session.id, "user" if i % 2 == 0 else "assistant", f"消息{i+1}")

        # 创建摘要
        await summary_repo.create(session.id, "摘要", 12)

        from app.memory.manager import MemoryManager
        manager = MemoryManager(message_repo, summary_repo, Mock())

        # Act
        context = await manager.get_context(session.id)

        # Assert
        assert len(context) == 4  # 摘要 + 3条消息
        # 验证是最近3条消息（消息10、11、12，索引9、10、11）
        assert "消息10" in context[1]["content"] or "消息11" in context[1]["content"] or "消息12" in context[1]["content"]

    @pytest.mark.asyncio
    async def test_get_context_returns_last_5_messages_without_summary(self):
        """验证无摘要时返回最近5条消息"""
        # Arrange
        user_repo = UserRepository()
        session_repo = SessionRepository()
        message_repo = MessageRepository()
        summary_repo = MemorySummaryRepository()

        password_hash = hash_password("password123")
        unique_id = str(uuid4())[:8]
        user = await user_repo.create(f"testuser_last5_{unique_id}", password_hash)
        session = await session_repo.create(user.id)

        # 创建7条消息
        for i in range(7):
            await message_repo.create(session.id, "user" if i % 2 == 0 else "assistant", f"消息{i+1}")

        from app.memory.manager import MemoryManager
        manager = MemoryManager(message_repo, summary_repo, Mock())

        # Act
        context = await manager.get_context(session.id)

        # Assert
        assert len(context) == 5  # 最近5条消息
        # 验证是最新的消息（消息3-7）
        contents = [msg["content"] for msg in context]
        assert any("消息7" in c for c in contents)  # 最新消息应该在里面
        assert any("消息6" in c for c in contents)


class TestExtractSummary:
    """测试 _extract_summary 方法"""

    def test_extract_summary_with_fullwidth_colon(self):
        """提取全角冒号'摘要：'之后的内容"""
        from app.memory.manager import MemoryManager

        manager = MemoryManager(Mock(), Mock(), Mock())
        content = "1. 分析请求\n2. 思考过程\n摘要：用户张三住在北京，养了一只金毛犬。"

        result = manager._extract_summary(content)

        assert result == "用户张三住在北京，养了一只金毛犬。"

    def test_extract_summary_with_halfwidth_colon(self):
        """提取半角冒号'摘要:'之后的内容"""
        from app.memory.manager import MemoryManager

        manager = MemoryManager(Mock(), Mock(), Mock())
        content = "分析过程...\n摘要: 这是一个简洁的摘要。"

        result = manager._extract_summary(content)

        assert result == "这是一个简洁的摘要。"

    def test_extract_summary_without_marker_returns_original(self):
        """没有标记时返回原文"""
        from app.memory.manager import MemoryManager

        manager = MemoryManager(Mock(), Mock(), Mock())
        content = "这是一段没有标记的内容"

        result = manager._extract_summary(content)

        assert result == "这是一段没有标记的内容"

    def test_extract_summary_empty_string(self):
        """空字符串返回空"""
        from app.memory.manager import MemoryManager

        manager = MemoryManager(Mock(), Mock(), Mock())

        assert manager._extract_summary("") == ""
        assert manager._extract_summary(None) == ""

    def test_extract_summary_removes_quotes(self):
        """去除引号和多余空白"""
        from app.memory.manager import MemoryManager

        manager = MemoryManager(Mock(), Mock(), Mock())
        content = '摘要："用户喜欢打篮球和足球"\n\n'

        result = manager._extract_summary(content)

        assert result == "用户喜欢打篮球和足球"

    def test_extract_summary_with_newlines(self):
        """处理多行内容"""
        from app.memory.manager import MemoryManager

        manager = MemoryManager(Mock(), Mock(), Mock())
        content = """分析过程：
1. 用户自我介绍
2. 用户爱好

摘要：用户王五住在北京，养了一只金毛犬豆豆。"""

        result = manager._extract_summary(content)

        assert result == "用户王五住在北京，养了一只金毛犬豆豆。"
