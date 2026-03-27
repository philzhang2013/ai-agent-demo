"""
智谱 AI Embedding API 测试
验证 embedding-3 接口正常工作
"""
import pytest
import os
from app.providers.embeddings import EmbeddingClient

# 使用有效的智谱 API Key（embedding 专用）
TEST_ZHIPUAI_API_KEY = "9b0054285834462a917a2f9d89418998.VsSCynh51xeeA7Ms"


class TestZhipuEmbedding:
    """测试智谱 Embedding API"""

    def test_embedding_single_text(self):
        """测试单条文本 embedding"""
        client = EmbeddingClient(
            api_key=TEST_ZHIPUAI_API_KEY,
            base_url="https://open.bigmodel.cn/api/paas/v4",
            model="embedding-3"
        )

        result = client.embed("这是一段测试文本")

        # 验证返回结果
        assert result is not None, "Embedding 不应返回 None"
        assert isinstance(result, list), "Embedding 应返回列表"
        assert len(result) == 2048, f"Embedding-3 默认维度应为 2048，实际为 {len(result)}"
        assert all(isinstance(x, float) for x in result), "所有元素应为浮点数"

    def test_embedding_chinese_text(self):
        """测试中文文本 embedding"""
        client = EmbeddingClient(
            api_key=TEST_ZHIPUAI_API_KEY,
            base_url="https://open.bigmodel.cn/api/paas/v4",
            model="embedding-3"
        )

        result = client.embed("你好，世界！这是一段中文测试文本。")

        assert result is not None
        assert len(result) == 2048

    def test_embedding_batch(self):
        """测试批量 embedding"""
        client = EmbeddingClient(
            api_key=TEST_ZHIPUAI_API_KEY,
            base_url="https://open.bigmodel.cn/api/paas/v4",
            model="embedding-3"
        )

        texts = ["第一段文本", "第二段文本", "第三段文本"]
        results = client.embed_batch(texts)

        assert len(results) == 3, "应返回 3 个 embedding"
        for i, result in enumerate(results):
            assert result is not None, f"第 {i} 个 embedding 不应为 None"
            assert len(result) == 2048, f"第 {i} 个 embedding 维度应为 2048"

    def test_embedding_empty_text(self):
        """测试空文本处理"""
        client = EmbeddingClient(
            api_key=TEST_ZHIPUAI_API_KEY,
            base_url="https://open.bigmodel.cn/api/paas/v4",
            model="embedding-3"
        )

        result = client.embed("")
        assert result is None, "空文本应返回 None"

        result = client.embed("   ")
        assert result is None, "空白文本应返回 None"

    def test_embedding_similarity(self):
        """测试语义相似度 - 相似文本应该有相似的 embedding"""
        import math

        client = EmbeddingClient(
            api_key=TEST_ZHIPUAI_API_KEY,
            base_url="https://open.bigmodel.cn/api/paas/v4",
            model="embedding-3"
        )

        # 获取两个相似文本的 embedding
        vec1 = client.embed("我喜欢吃苹果")
        vec2 = client.embed("我爱吃苹果")
        # 不相关的文本
        vec3 = client.embed("今天天气很好")

        assert vec1 is not None and vec2 is not None and vec3 is not None

        # 计算余弦相似度
        def cosine_similarity(a, b):
            dot = sum(x*y for x, y in zip(a, b))
            norm_a = math.sqrt(sum(x*x for x in a))
            norm_b = math.sqrt(sum(x*x for x in b))
            return dot / (norm_a * norm_b)

        sim_similar = cosine_similarity(vec1, vec2)
        sim_different = cosine_similarity(vec1, vec3)

        # 相似文本的相似度应该更高
        assert sim_similar > sim_different, \
            f"相似文本的相似度({sim_similar:.4f})应大于不相关文本({sim_different:.4f})"


class TestZhipuEmbeddingConfig:
    """测试 Embedding 配置集成"""

    def test_settings_have_embedding_config(self):
        """测试配置中包含 embedding 配置项"""
        from app.config import get_settings
        settings = get_settings()

        assert hasattr(settings, 'embedding_provider')
        assert hasattr(settings, 'embedding_api_key')
        assert hasattr(settings, 'embedding_base_url')
        assert hasattr(settings, 'embedding_model')

    def test_default_embedding_config(self):
        """测试默认 embedding 配置"""
        from app.config import get_settings
        settings = get_settings()

        assert settings.embedding_provider == "zhipuai"
        assert settings.embedding_model == "embedding-3"
        assert "bigmodel.cn" in settings.embedding_base_url
