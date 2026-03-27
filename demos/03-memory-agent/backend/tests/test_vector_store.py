"""
VectorStore 测试
TDD: 先写测试，再实现代码

向量存储功能：
- 生成文本的向量嵌入（通过外部 Embedding API）
- 存储向量到数据库
- 语义相似度搜索
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from app.memory.vector_store import VectorStore


class TestVectorStore:
    """测试 VectorStore"""

    @pytest.fixture
    def mock_embedding_client(self):
        """创建模拟的 Embedding 客户端"""
        client = Mock()
        # 模拟返回 2048 维向量（智谱 embedding-3）
        client.embed.return_value = [0.1] * 2048
        return client

    @pytest.fixture
    def store(self, mock_embedding_client):
        """创建 VectorStore 实例"""
        return VectorStore(embedding_client=mock_embedding_client)

    def test_embed_text(self, store, mock_embedding_client):
        """测试生成文本向量"""
        # Act
        embedding = store.embed("测试文本")

        # Assert
        assert len(embedding) == 2048
        assert embedding[0] == 0.1
        mock_embedding_client.embed.assert_called_once_with("测试文本")

    def test_embed_batch(self, store, mock_embedding_client):
        """测试批量生成向量"""
        # Arrange
        texts = ["文本1", "文本2", "文本3"]
        mock_embedding_client.embed_batch.return_value = [
            [0.1] * 2048,
            [0.2] * 2048,
            [0.3] * 2048
        ]

        # Act
        embeddings = store.embed_batch(texts)

        # Assert
        assert len(embeddings) == 3
        assert len(embeddings[0]) == 2048
        mock_embedding_client.embed_batch.assert_called_once_with(texts)

    def test_cosine_similarity(self, store):
        """测试余弦相似度计算"""
        # Arrange
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        vec3 = [0.0, 1.0, 0.0]

        # Act & Assert
        assert store.cosine_similarity(vec1, vec2) == 1.0
        assert store.cosine_similarity(vec1, vec3) == 0.0

        # 相同向量相似度为 1
        same_vec = [0.5, 0.5, 0.5]
        assert abs(store.cosine_similarity(same_vec, same_vec) - 1.0) < 0.001

    def test_cosine_similarity_different_lengths(self, store):
        """测试不同长度向量的相似度计算"""
        # 不同长度的向量应该截断或填充
        vec1 = [1.0, 0.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]

        similarity = store.cosine_similarity(vec1, vec2)
        # 应该使用公共长度的部分计算
        assert 0 <= similarity <= 1

    @pytest.mark.asyncio
    async def test_store_message_embedding(self, store, mock_embedding_client):
        """测试存储消息向量"""
        # Arrange
        message_id = "msg-123"
        content = "测试消息内容"

        # Act
        result = await store.store_message_embedding(message_id, content)

        # Assert
        assert result is True
        mock_embedding_client.embed.assert_called_once_with(content)

    @pytest.mark.asyncio
    async def test_store_segment_embedding(self, store, mock_embedding_client):
        """测试存储主题段向量"""
        # Arrange
        segment_id = "seg-456"
        summary = "这是一个主题段摘要"

        # Act
        result = await store.store_segment_embedding(segment_id, summary)

        # Assert
        assert result is True
        mock_embedding_client.embed.assert_called_once_with(summary)

    def test_find_similar_vectors(self, store):
        """测试查找相似向量"""
        # Arrange
        query_embedding = [1.0, 0.0, 0.0] + [0.0] * 2045
        candidates = [
            ("id1", [1.0, 0.0, 0.0] + [0.0] * 2045),  # 完全相同
            ("id2", [0.9, 0.1, 0.0] + [0.0] * 2045),  # 较相似
            ("id3", [0.0, 1.0, 0.0] + [0.0] * 2045),  # 不太相似（正交）
        ]

        # Act
        results = store.find_similar(
            query_embedding=query_embedding,
            candidates=candidates,
            top_k=2
        )

        # Assert
        assert len(results) == 2
        assert results[0][0] == "id1"  # 最相似
        assert results[0][1] > 0.99  # 高相似度
        assert results[1][0] == "id2"  # 第二相似

    def test_normalize_vector(self, store):
        """测试向量归一化"""
        # Arrange
        vec = [3.0, 4.0, 0.0]

        # Act
        normalized = store.normalize(vec)

        # Assert
        assert len(normalized) == 3
        assert abs(normalized[0] - 0.6) < 0.001
        assert abs(normalized[1] - 0.8) < 0.001
        assert normalized[2] == 0.0

    def test_empty_embedding_client(self):
        """测试没有 Embedding 客户端时的行为"""
        store = VectorStore(embedding_client=None)

        # 应该返回 None 或空列表
        result = store.embed("测试")
        assert result is None or result == []

    @pytest.mark.asyncio
    async def test_store_without_embedding_client(self):
        """测试没有客户端时存储失败"""
        store = VectorStore(embedding_client=None)

        result = await store.store_message_embedding("msg-1", "内容")
        assert result is False
