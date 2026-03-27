"""
ImportanceScorer 测试
TDD: 先写测试，再实现代码

语义重要性评分逻辑：
- 高频主题关键词 → 提升分数
- 否定、修正 → 高分（关键信息）
- 闲聊 → 降低分数
"""
import pytest
from app.memory.importance_scorer import ImportanceScorer


class TestImportanceScorer:
    """测试 ImportanceScorer"""

    @pytest.fixture
    def scorer(self):
        """创建评分器实例"""
        return ImportanceScorer()

    def test_basic_scoring(self, scorer):
        """测试基础评分功能"""
        # Arrange
        message = "这是一个普通的测试消息"

        # Act
        score = scorer.score(message)

        # Assert
        assert 0.0 <= score <= 1.0
        assert isinstance(score, float)

    def test_keyword_importance(self, scorer):
        """测试关键词对重要性评分的影响"""
        # 技术关键词应该获得更高分数
        tech_message = "我们需要使用 Python 和 PostgreSQL 来构建后端 API"
        casual_message = "你好，今天天气不错"

        tech_score = scorer.score(tech_message)
        casual_score = scorer.score(casual_message)

        # 技术消息应该比闲聊消息分数高
        assert tech_score > casual_score

    def test_correction_detection(self, scorer):
        """测试检测修正/否定语句"""
        # 修正语句应该是高分
        correction = "不对，我刚才说错了，正确的答案应该是 42"
        score = scorer.score(correction)

        # 修正语句应该获得较高分数
        assert score > 0.7

    def test_question_importance(self, scorer):
        """测试问题的评分"""
        # 关键问题
        important_question = "这个架构设计的安全性如何保证？"
        # 闲聊问题
        casual_question = "你今天过得怎么样？"

        important_score = scorer.score(important_question)
        casual_score = scorer.score(casual_question)

        # 关键问题应该分数更高
        assert important_score > casual_score

    def test_length_factor(self, scorer):
        """测试消息长度对评分的影响"""
        # 太长或太短的消息应该分数较低
        very_short = "好的"
        very_long = "这是一个" * 100 + "非常长的消息"
        moderate = "这是一个关于如何实现用户认证功能的详细讨论"

        short_score = scorer.score(very_short)
        long_score = scorer.score(very_long)
        moderate_score = scorer.score(moderate)

        # 适中长度的消息应该有合理的分数
        assert 0.3 <= moderate_score <= 0.9

    def test_entity_recognition(self, scorer):
        """测试命名实体识别提升分数"""
        # 包含具体实体
        with_entities = "OpenAI 发布了 GPT-4 模型，Google 推出了 Bard"
        # 无具体实体
        without_entities = "很多公司都在开发人工智能产品"

        entity_score = scorer.score(with_entities)
        no_entity_score = scorer.score(without_entities)

        # 包含实体的消息分数应该更高
        assert entity_score > no_entity_score

    def test_action_words(self, scorer):
        """测试动作词汇提升分数"""
        # 包含动作词
        with_action = "我们必须实现缓存机制，部署到生产环境"
        # 无动作词
        without_action = "关于缓存机制有一些想法"

        action_score = scorer.score(with_action)
        no_action_score = scorer.score(without_action)

        # 包含动作词的消息分数应该更高
        assert action_score > no_action_score

    def test_score_batch(self, scorer):
        """测试批量评分"""
        messages = [
            "这是一个普通消息",
            "我们必须立即修复这个严重的安全漏洞！",
            "好的",
            "根据之前讨论的架构方案，我们需要使用 Redis 作为缓存层"
        ]

        scores = scorer.score_batch(messages)

        # 返回的分数数量应该与消息数量相同
        assert len(scores) == len(messages)
        # 所有分数应该在 0-1 范围内
        assert all(0.0 <= s <= 1.0 for s in scores)
        # 安全漏洞消息应该是最高分
        assert scores[1] > scores[0]
        assert scores[1] > scores[2]
