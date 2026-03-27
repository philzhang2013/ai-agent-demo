"""
重要性评分器
基于规则的消息重要性评估
"""
import re
from typing import List


class ImportanceScorer:
    """
    语义重要性评分器

    评分维度：
    - 关键词密度（技术词汇、业务术语）
    - 语句类型（问题、修正、否定、动作）
    - 实体密度（命名实体、专有名词）
    - 长度适中度
    """

    # 高权重技术关键词
    TECH_KEYWORDS = {
        'python', 'java', 'javascript', 'typescript', 'go', 'rust', 'sql',
        'postgresql', 'mysql', 'redis', 'mongodb', 'docker', 'kubernetes',
        'api', 'rest', 'graphql', 'grpc', 'http', 'https',
        'database', 'cache', 'server', 'client', 'backend', 'frontend',
        'authentication', 'authorization', 'security', 'encryption',
        'algorithm', 'data structure', 'architecture', 'microservice',
        'async', 'await', 'concurrent', 'threading', 'performance',
        'github', 'git', 'ci/cd', 'devops', 'testing', 'debug'
    }

    # 业务关键词
    BUSINESS_KEYWORDS = {
        '用户', '客户', '产品', '服务', '功能', '需求',
        '设计', '实现', '开发', '测试', '部署', '发布',
        '问题', 'bug', '修复', '优化', '改进', '重构'
    }

    # 高重要性标记词
    IMPORTANT_MARKERS = {
        '必须', '需要', '应该', '重要', '关键', '核心',
        '严重', '紧急', '立即', '务必', '注意', '警告',
        '修复', '解决', 'bug', '漏洞', '安全问题'
    }

    # 修正/否定标记词
    CORRECTION_MARKERS = {
        '不对', '错误', '更正', '纠正', '修正',
        '抱歉', '说错了', '不是', '而是', '正确的是'
    }

    # 动作动词
    ACTION_WORDS = {
        '实现', '创建', '构建', '开发', '部署', '发布',
        '修复', '解决', '优化', '重构', '测试', '验证',
        '实现', '完成', '提交', '合并', '更新', '删除'
    }

    # 闲聊/低重要性模式
    CASUAL_PATTERNS = [
        r'你好', r'在吗', r'在干嘛', r'吃饭了吗', r'早上好', r'晚上好',
        r'谢谢', r'不客气', r'好的', r'嗯', r'哦', r'啊',
        r'今天.*怎么样', r'天气.*怎样', r'周末.*计划'
    ]

    def score(self, message: str) -> float:
        """
        对单条消息进行重要性评分

        Returns:
            0.0 - 1.0 之间的重要性分数
        """
        if not message or not message.strip():
            return 0.0

        scores = []

        # 1. 基础长度评分（适中长度最佳）
        length_score = self._score_length(message)
        scores.append(length_score * 0.15)

        # 2. 关键词密度评分
        keyword_score = self._score_keywords(message)
        scores.append(keyword_score * 0.25)

        # 3. 语句类型评分
        type_score = self._score_sentence_type(message)
        scores.append(type_score * 0.25)

        # 4. 实体密度评分
        entity_score = self._score_entities(message)
        scores.append(entity_score * 0.20)

        # 5. 动作词评分
        action_score = self._score_actions(message)
        scores.append(action_score * 0.15)

        # 综合评分
        final_score = sum(scores)

        # 闲聊模式检测 - 大幅降低分数
        if self._is_casual(message):
            final_score *= 0.3

        # 修正/否定检测 - 大幅提升分数
        if self._is_correction(message):
            final_score = min(1.0, final_score * 1.5 + 0.2)

        # 重要标记检测 - 提升分数
        if self._has_important_marker(message):
            final_score = min(1.0, final_score * 1.3 + 0.1)

        return round(max(0.0, min(1.0, final_score)), 3)

    def score_batch(self, messages: List[str]) -> List[float]:
        """批量评分"""
        return [self.score(msg) for msg in messages]

    def _score_length(self, message: str) -> float:
        """根据长度评分（适中长度最佳）"""
        length = len(message)

        if length < 5:
            return 0.2
        elif length < 20:
            return 0.5
        elif length < 100:
            return 0.9
        elif length < 300:
            return 1.0
        elif length < 500:
            return 0.8
        else:
            return 0.6

    def _score_keywords(self, message: str) -> float:
        """评分关键词密度"""
        message_lower = message.lower()
        words = set(re.findall(r'\b\w+\b', message_lower))

        tech_matches = len(words & self.TECH_KEYWORDS)
        business_matches = len(
            [k for k in self.BUSINESS_KEYWORDS if k in message]
        )

        total_keywords = tech_matches + business_matches

        if total_keywords == 0:
            return 0.3
        elif total_keywords <= 2:
            return 0.5
        elif total_keywords <= 4:
            return 0.7
        elif total_keywords <= 6:
            return 0.85
        else:
            return 1.0

    def _score_sentence_type(self, message: str) -> float:
        """根据语句类型评分"""
        score = 0.5

        # 问题检测
        if '?' in message or '？' in message:
            # 技术问题分数更高
            if any(kw in message.lower() for kw in self.TECH_KEYWORDS):
                score = 0.75
            else:
                score = 0.55

        # 命令/祈使句
        if re.search(r'(请|务必|必须|需要|应该)\s*', message):
            score = max(score, 0.7)

        # 陈述句包含具体技术内容
        if len(re.findall(r'\b\w{4,}\b', message)) >= 3:
            score = max(score, 0.65)

        return score

    def _score_entities(self, message: str) -> float:
        """评分命名实体密度"""
        # 大写字母开头的连续词（英文专有名词）
        english_entities = len(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', message))

        # 中文专有名词（简单的启发式规则）
        chinese_entities = len(re.findall(r'[\u4e00-\u9fa5]{2,}(?:公司|平台|系统|框架|技术|语言)', message))

        # 版本号
        versions = len(re.findall(r'\d+\.\d+(?:\.\d+)?', message))

        total_entities = english_entities + chinese_entities + versions

        if total_entities == 0:
            return 0.3
        elif total_entities <= 2:
            return 0.6
        elif total_entities <= 4:
            return 0.8
        else:
            return 1.0

    def _score_actions(self, message: str) -> float:
        """评分动作词"""
        action_count = sum(1 for action in self.ACTION_WORDS if action in message)

        if action_count == 0:
            return 0.3
        elif action_count == 1:
            return 0.6
        elif action_count == 2:
            return 0.8
        else:
            return 1.0

    def _is_casual(self, message: str) -> bool:
        """检测是否为闲聊消息"""
        for pattern in self.CASUAL_PATTERNS:
            if re.search(pattern, message):
                return True
        return False

    def _is_correction(self, message: str) -> bool:
        """检测是否为修正/否定语句"""
        return any(marker in message for marker in self.CORRECTION_MARKERS)

    def _has_important_marker(self, message: str) -> bool:
        """检测是否包含重要标记词"""
        return any(marker in message for marker in self.IMPORTANT_MARKERS)
