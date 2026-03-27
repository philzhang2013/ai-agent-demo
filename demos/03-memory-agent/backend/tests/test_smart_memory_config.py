"""
SmartMemoryManager 配置测试
TDD: 先写测试，再实现代码
"""
import pytest
from unittest.mock import Mock, patch
from app.memory.config import SmartMemoryConfig, create_smart_memory_manager


class TestSmartMemoryConfig:
    """测试 SmartMemoryConfig"""

    def test_default_configuration(self):
        """测试默认配置"""
        # Arrange & Act
        config = SmartMemoryConfig()

        # Assert
        assert config.similarity_threshold == 0.7
        assert config.max_segment_messages == 10
        assert config.max_segment_duration_minutes == 30
        assert config.importance_threshold == 0.7
        assert config.enable_semantic_search is True
        assert config.enable_auto_segmentation is True

    def test_custom_configuration(self):
        """测试自定义配置"""
        # Arrange & Act
        config = SmartMemoryConfig(
            similarity_threshold=0.5,
            max_segment_messages=5,
            importance_threshold=0.8
        )

        # Assert
        assert config.similarity_threshold == 0.5
        assert config.max_segment_messages == 5
        assert config.importance_threshold == 0.8

    def test_from_dict(self):
        """测试从字典创建配置"""
        # Arrange
        config_dict = {
            "similarity_threshold": 0.6,
            "max_segment_messages": 8,
            "enable_semantic_search": False
        }

        # Act
        config = SmartMemoryConfig.from_dict(config_dict)

        # Assert
        assert config.similarity_threshold == 0.6
        assert config.max_segment_messages == 8
        assert config.enable_semantic_search is False
        # 未指定的保持默认值
        assert config.importance_threshold == 0.7

    def test_to_dict(self):
        """测试配置转字典"""
        # Arrange
        config = SmartMemoryConfig(
            similarity_threshold=0.8,
            max_segment_messages=15
        )

        # Act
        config_dict = config.to_dict()

        # Assert
        assert config_dict["similarity_threshold"] == 0.8
        assert config_dict["max_segment_messages"] == 15
        assert "importance_threshold" in config_dict


class TestCreateSmartMemoryManager:
    """测试创建 SmartMemoryManager"""

    @pytest.mark.asyncio
    async def test_create_with_default_config(self):
        """测试使用默认配置创建"""
        # Act
        manager = await create_smart_memory_manager()

        # Assert
        assert manager is not None
        assert manager.importance_scorer is not None
        assert manager.topic_segmenter is not None

    @pytest.mark.asyncio
    async def test_create_with_custom_config(self):
        """测试使用自定义配置创建"""
        # Arrange
        config = SmartMemoryConfig(
            similarity_threshold=0.5,
            max_segment_messages=5
        )

        # Act
        manager = await create_smart_memory_manager(config)

        # Assert
        assert manager is not None
        assert manager.topic_segmenter.similarity_threshold == 0.5
        assert manager.topic_segmenter.max_segment_messages == 5

    @pytest.mark.asyncio
    async def test_create_with_disabled_features(self):
        """测试禁用某些功能的配置"""
        # Arrange
        config = SmartMemoryConfig(
            enable_semantic_search=False,
            enable_auto_segmentation=False
        )

        # Act
        manager = await create_smart_memory_manager(config)

        # Assert
        assert manager is not None
        # 禁用语义搜索时 vector_store 应该为 None
        assert manager.vector_store is None
