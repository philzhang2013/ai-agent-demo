"""
向量嵌入客户端
支持 Kimi / 智谱 AI Embedding API
"""
import logging
import httpx
from typing import List, Optional

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """
    向量嵌入客户端

    支持 Kimi 和智谱 AI 的 Embedding API
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.moonshot.cn/v1",
        model: str = "moonshot-v1-embedding"
    ):
        """
        初始化 Embedding 客户端

        Args:
            api_key: API Key (Kimi 或智谱)
            base_url: API 基础 URL
            model: 使用的模型名称，Kimi 默认 moonshot-v1-embedding，智谱默认 embedding-2
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.embeddings_url = f"{base_url}/embeddings"

    def embed(self, text: str) -> Optional[List[float]]:
        """
        生成单个文本的向量嵌入（同步）

        Args:
            text: 输入文本

        Returns:
            向量列表，失败返回 None
        """
        if not text or not text.strip():
            logger.warning("[Embedding] 输入文本为空")
            return None

        try:
            # 调用 Embedding API
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    self.embeddings_url,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json={
                        "model": self.model,
                        "input": text.strip()
                    }
                )

                if response.status_code != 200:
                    logger.error(f"[Embedding] API 错误: {response.status_code} - {response.text}")
                    return None

                data = response.json()

                # 检查错误
                if "error" in data:
                    logger.error(f"[Embedding] API 返回错误: {data['error']}")
                    return None

                # 提取向量
                if "data" not in data or not data["data"]:
                    logger.error("[Embedding] API 响应中没有 data 字段")
                    return None

                embedding = data["data"][0].get("embedding")
                if not embedding:
                    logger.error("[Embedding] 响应中没有 embedding 字段")
                    return None

                logger.debug(f"[Embedding] 成功生成向量，维度: {len(embedding)}")
                return embedding

        except httpx.TimeoutException:
            logger.error("[Embedding] 请求超时")
            return None
        except Exception as e:
            logger.error(f"[Embedding] 请求失败: {e}")
            return None

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量生成向量嵌入

        Args:
            texts: 文本列表

        Returns:
            向量列表
        """
        results = []
        for text in texts:
            embedding = self.embed(text)
            if embedding:
                results.append(embedding)
            else:
                # 失败时返回零向量
                logger.warning(f"[Embedding] 文本 '{text[:50]}...' 嵌入失败，使用零向量")
                results.append([0.0] * len(results[0]) if results else [0.0] * 1024)

        return results
