"""
智能记忆管理器配置
提供配置类和工厂函数
"""
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from datetime import timedelta

from app.memory.smart_memory_manager import SmartMemoryManager
from app.memory.importance_scorer import ImportanceScorer
from app.memory.topic_segmenter import TopicSegmenter
from app.memory.vector_store import VectorStore
from app.db.repositories import ImportanceScoreRepository, MemorySegmentRepository
from app.providers.embeddings import EmbeddingClient
from app.config import get_settings


@dataclass
class SmartMemoryConfig:
    """
    智能记忆管理器配置

    Attributes:
        similarity_threshold: 主题分段相似度阈值
        max_segment_messages: 单个主题段最大消息数
        max_segment_duration_minutes: 主题段最大持续时间（分钟）
        importance_threshold: 高重要性消息阈值
        enable_semantic_search: 是否启用语义搜索
        enable_auto_segmentation: 是否启用自动分段
        embedding_dimension: 向量嵌入维度
    """
    similarity_threshold: float = 0.7
    max_segment_messages: int = 10
    max_segment_duration_minutes: int = 30
    importance_threshold: float = 0.7
    enable_semantic_search: bool = True  # 启用语义搜索（需要有效的 embedding API key）
    enable_auto_segmentation: bool = True
    embedding_dimension: int = 2048  # 智谱 embedding-3 默认维度

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "SmartMemoryConfig":
        """从字典创建配置"""
        # 过滤掉不支持的字段
        valid_fields = {k: v for k, v in config_dict.items() if k in cls.__dataclass_fields__}
        return cls(**valid_fields)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @property
    def max_segment_duration(self) -> timedelta:
        """获取最大分段持续时间"""
        return timedelta(minutes=self.max_segment_duration_minutes)


async def create_smart_memory_manager(
    config: Optional[SmartMemoryConfig] = None
) -> SmartMemoryManager:
    """
    创建并配置 SmartMemoryManager

    Args:
        config: 配置对象，如果为 None 则使用默认配置

    Returns:
        配置好的 SmartMemoryManager 实例
    """
    if config is None:
        config = SmartMemoryConfig()

    # 创建评分器和分段器
    importance_scorer = ImportanceScorer()
    topic_segmenter = TopicSegmenter(
        similarity_threshold=config.similarity_threshold,
        max_segment_messages=config.max_segment_messages,
        max_segment_duration=config.max_segment_duration
    )

    # 可选组件
    vector_store = None
    if config.enable_semantic_search:
        # 创建 Embedding 客户端（使用独立的 embedding 配置）
        settings = get_settings()

        # 确定 embedding 配置
        embedding_provider = settings.embedding_provider
        embedding_api_key = settings.embedding_api_key or (
            settings.zhipuai_api_key if embedding_provider == "zhipuai" else settings.kimi_api_key
        )
        embedding_base_url = settings.embedding_base_url
        embedding_model = settings.embedding_model

        if embedding_provider == "zhipuai":
            embedding_client = EmbeddingClient(
                api_key=embedding_api_key,
                base_url=embedding_base_url,
                model=embedding_model
            )
        elif embedding_provider == "kimi":
            embedding_client = EmbeddingClient(
                api_key=embedding_api_key,
                base_url="https://api.moonshot.cn/v1",
                model="moonshot-v1-embedding"
            )
        else:
            raise ValueError(f"不支持的 embedding 提供商: {embedding_provider}")

        vector_store = VectorStore(embedding_client=embedding_client)

    # 数据访问层
    importance_repo = ImportanceScoreRepository()
    segment_repo = MemorySegmentRepository()

    # 创建管理器
    manager = SmartMemoryManager(
        importance_scorer=importance_scorer,
        topic_segmenter=topic_segmenter,
        vector_store=vector_store,
        importance_repo=importance_repo,
        segment_repo=segment_repo,
    )

    return manager
