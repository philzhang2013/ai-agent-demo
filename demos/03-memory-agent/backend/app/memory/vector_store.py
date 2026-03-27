"""
向量存储组件
管理文本的向量嵌入和相似度搜索
"""
import math
from typing import List, Tuple, Optional, Callable


class VectorStore:
    """
    向量存储

    功能：
    1. 通过 Embedding API 生成文本向量
    2. 计算向量相似度
    3. 存储和检索向量
    """

    def __init__(self, embedding_client: Optional[Callable] = None):
        """
        初始化向量存储

        Args:
            embedding_client: Embedding API 客户端，需要实现 embed() 和 embed_batch() 方法
        """
        self.embedding_client = embedding_client

    def embed(self, text: str) -> Optional[List[float]]:
        """
        生成单个文本的向量嵌入

        Args:
            text: 输入文本

        Returns:
            1536 维向量，如果客户端未设置则返回 None
        """
        if self.embedding_client is None:
            return None

        return self.embedding_client.embed(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量生成文本的向量嵌入

        Args:
            texts: 文本列表

        Returns:
            向量列表
        """
        if self.embedding_client is None:
            return []

        return self.embedding_client.embed_batch(texts)

    def cosine_similarity(
        self,
        vec1: List[float],
        vec2: List[float]
    ) -> float:
        """
        计算两个向量的余弦相似度

        Args:
            vec1: 向量1
            vec2: 向量2

        Returns:
            余弦相似度（-1 到 1）
        """
        # 处理长度不一致的情况
        min_len = min(len(vec1), len(vec2))
        v1 = vec1[:min_len]
        v2 = vec2[:min_len]

        if not v1 or not v2:
            return 0.0

        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(a * a for a in v2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def normalize(self, vec: List[float]) -> List[float]:
        """
        向量归一化

        Args:
            vec: 输入向量

        Returns:
            单位向量
        """
        norm = math.sqrt(sum(a * a for a in vec))

        if norm == 0:
            return [0.0] * len(vec)

        return [a / norm for a in vec]

    def find_similar(
        self,
        query_embedding: List[float],
        candidates: List[Tuple[str, List[float]]],
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Tuple[str, float]]:
        """
        查找与查询向量最相似的向量

        Args:
            query_embedding: 查询向量
            candidates: [(id, embedding), ...] 候选向量列表
            top_k: 返回最相似的前 k 个
            threshold: 相似度阈值，低于此值的被过滤

        Returns:
            [(id, similarity), ...] 按相似度降序排列
        """
        similarities = []

        for candidate_id, candidate_embedding in candidates:
            sim = self.cosine_similarity(query_embedding, candidate_embedding)
            if sim >= threshold:
                similarities.append((candidate_id, sim))

        # 按相似度降序排序
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    async def store_message_embedding(
        self,
        message_id: str,
        content: str
    ) -> bool:
        """
        存储消息的向量嵌入

        Args:
            message_id: 消息 ID
            content: 消息内容

        Returns:
            是否成功
        """
        if self.embedding_client is None:
            return False

        try:
            embedding = self.embed(content)
            if embedding is None:
                return False

            # 实际存储由调用方（如 ImportanceScoreRepository）完成
            return True
        except Exception:
            return False

    async def store_segment_embedding(
        self,
        segment_id: str,
        summary: str
    ) -> bool:
        """
        存储主题段的向量嵌入

        Args:
            segment_id: 主题段 ID
            summary: 摘要内容

        Returns:
            是否成功
        """
        if self.embedding_client is None:
            return False

        try:
            embedding = self.embed(summary)
            if embedding is None:
                return False

            # 实际存储由调用方完成
            return True
        except Exception:
            return False

    def euclidean_distance(
        self,
        vec1: List[float],
        vec2: List[float]
    ) -> float:
        """
        计算欧氏距离

        Args:
            vec1: 向量1
            vec2: 向量2

        Returns:
            欧氏距离
        """
        min_len = min(len(vec1), len(vec2))
        v1 = vec1[:min_len]
        v2 = vec2[:min_len]

        return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))
