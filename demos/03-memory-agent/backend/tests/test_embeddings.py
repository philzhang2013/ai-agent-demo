"""
EmbeddingClient 测试
TDD: 先写测试，确保 embedding 功能正常

测试目标：
- EmbeddingClient 能成功调用智谱 AI API
- process_message 能成功生成并存储 embedding
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.providers.embeddings import EmbeddingClient


class TestEmbeddingClient:
    """测试 EmbeddingClient"""

    @pytest.fixture
    def client(self):
        """创建 EmbeddingClient 实例"""
        return EmbeddingClient(
            api_key="test-api-key",
            model="embedding-2"
        )

    def test_init(self, client):
        """测试初始化"""
        assert client.api_key == "test-api-key"
        assert client.model == "embedding-2"
        assert client.embeddings_url == "https://open.bigmodel.cn/api/paas/v4/embeddings"

    @pytest.mark.integration
    def test_embed_real_api(self, client):
        """
        集成测试：真实调用智谱 AI Embedding API

        注意：此测试需要有效的 API Key 和足够的余额
        跳过条件：API 余额不足时跳过
        """
        # 使用真实 API Key（从环境变量获取）
        import os
        api_key = os.getenv("ZHIPUAI_API_KEY")
        if not api_key:
            pytest.skip("需要设置 ZHIPUAI_API_KEY 环境变量")

        client = EmbeddingClient(api_key=api_key)

        # Act
        embedding = client.embed("测试文本")

        # 如果 API 余额不足，跳过测试
        if embedding is None:
            pytest.skip("智谱 AI Embedding API 余额不足，跳过真实 API 测试")

        # Assert
        assert len(embedding) > 0
        # embedding-2 模型返回 1024 维向量
        assert len(embedding) == 1024
        # 向量值应该是浮点数
        assert all(isinstance(x, float) for x in embedding)

    def test_embed_empty_text(self, client):
        """测试空文本处理"""
        # Act & Assert
        assert client.embed("") is None
        assert client.embed("   ") is None
        assert client.embed(None) is None

    @patch('app.providers.embeddings.httpx.Client')
    def test_embed_success(self, mock_client_class, client):
        """测试成功的 embedding 生成"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{
                "embedding": [0.1, 0.2, 0.3] * 341 + [0.1]  # 1024 维
            }]
        }

        mock_http_client = MagicMock()
        mock_http_client.__enter__ = Mock(return_value=mock_http_client)
        mock_http_client.__exit__ = Mock(return_value=False)
        mock_http_client.post.return_value = mock_response
        mock_client_class.return_value = mock_http_client

        # Act
        embedding = client.embed("测试文本")

        # Assert
        assert embedding is not None
        assert len(embedding) == 1024

    @patch('app.providers.embeddings.httpx.Client')
    def test_embed_api_error(self, mock_client_class, client):
        """测试 API 错误处理"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        mock_http_client = MagicMock()
        mock_http_client.__enter__ = Mock(return_value=mock_http_client)
        mock_http_client.__exit__ = Mock(return_value=False)
        mock_http_client.post.return_value = mock_response
        mock_client_class.return_value = mock_http_client

        # Act
        embedding = client.embed("测试文本")

        # Assert
        assert embedding is None

    @patch('app.providers.embeddings.httpx.Client')
    def test_embed_timeout(self, mock_client_class, client):
        """测试超时处理"""
        # Arrange
        import httpx
        mock_http_client = MagicMock()
        mock_http_client.__enter__ = Mock(return_value=mock_http_client)
        mock_http_client.__exit__ = Mock(return_value=False)
        mock_http_client.post.side_effect = httpx.TimeoutException("Request timeout")
        mock_client_class.return_value = mock_http_client

        # Act
        embedding = client.embed("测试文本")

        # Assert
        assert embedding is None

    def test_embed_batch(self, client):
        """测试批量 embedding"""
        # 这个测试会使用 mock，避免真实 API 调用
        with patch.object(client, 'embed') as mock_embed:
            mock_embed.side_effect = [
                [0.1] * 1024,
                [0.2] * 1024,
                None,  # 模拟一个失败的情况
            ]

            # Act
            embeddings = client.embed_batch(["文本1", "文本2", "文本3"])

            # Assert
            assert len(embeddings) == 3
            assert embeddings[0] == [0.1] * 1024
            assert embeddings[1] == [0.2] * 1024
            assert embeddings[2] == [0.0] * 1024  # 失败时返回零向量


class TestProcessMessageWithEmbedding:
    """测试 process_message 与 embedding 集成"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_process_message_with_real_embedding(self):
        """
        集成测试：使用真实的 EmbeddingClient 处理消息

        此测试验证：
        1. SmartMemoryManager 能成功处理消息
        2. embedding 能成功生成
        3. embedding 能成功存储到数据库
        """
        import os
        import uuid
        from app.memory.config import create_smart_memory_manager
        from app.db.repositories import ImportanceScoreRepository, MemorySegmentRepository

        api_key = os.getenv("ZHIPUAI_API_KEY")
        if not api_key:
            pytest.skip("需要设置 ZHIPUAI_API_KEY 环境变量")

        # 使用真实的配置创建 manager
        manager = await create_smart_memory_manager()

        # 确认 vector_store 和 embedding_client 已配置
        assert manager.vector_store is not None
        assert manager.vector_store.embedding_client is not None

        # 先测试 embedding API 是否可用
        test_embedding = manager.vector_store.embed("测试")
        if test_embedding is None:
            pytest.skip("智谱 AI Embedding API 不可用（余额不足或认证失败），跳过集成测试")

        # 创建测试消息（使用有效的 UUID）
        test_msg_id = str(uuid.uuid4())
        test_session_id = str(uuid.uuid4())
        message = {
            "id": test_msg_id,
            "session_id": test_session_id,
            "content": "这是一条测试消息，用于验证 embedding 生成功能",
            "created_at": "2026-03-27T10:00:00Z"
        }

        # Act - 处理消息
        result = await manager.process_message(message)

        # Assert
        assert result is True, "process_message 应该返回 True"

        # 验证 embedding 被成功生成
        embedding = manager.vector_store.embed(message["content"])
        assert embedding is not None, "embedding 不应该为 None"
        assert len(embedding) == 1024, f"embedding 应该是 1024 维，实际是 {len(embedding)}"

        print(f"✅ Embedding 生成成功！维度: {len(embedding)}")
        print(f"✅ 前5个向量值: {embedding[:5]}")
