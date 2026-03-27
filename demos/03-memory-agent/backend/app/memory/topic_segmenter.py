"""
主题分割器
将对话按主题切分为多个段落
"""
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

from app.memory.importance_scorer import ImportanceScorer


@dataclass
class TopicSegment:
    """主题段数据类"""
    topic_name: str
    start_message_id: str
    end_message_id: str
    message_count: int
    importance_score: float
    summary: str


class TopicSegmenter:
    """
    主题分割器

    分段策略：
    1. 语义相似度低于阈值 → 新主题
    2. 消息数超过限制 → 强制分段
    3. 时间间隔过大 → 强制分段
    """

    # 主题关键词映射
    TOPIC_KEYWORDS = {
        "数据库": ["database", "sql", "postgresql", "mysql", "redis", "mongodb", "查询", "索引", "表", "explain", "analyze"],
        "API设计": ["api", "rest", "graphql", "http", "接口", "端点", "endpoint", "路由"],
        "认证授权": ["auth", "authentication", "authorization", "登录", "权限", "jwt", "token", "oauth"],
        "缓存": ["cache", "redis", "memcached", "缓存", "命中率", "穿透", "雪崩", "布隆过滤器"],
        "架构": ["architecture", "microservice", "monolith", "架构", "微服务", "单体", "分布式", "决策"],
        "性能优化": ["performance", "optimization", "optimize", "性能", "优化", "慢查询", "瓶颈"],
        "部署": ["deploy", "deployment", "docker", "kubernetes", "k8s", "ci/cd", "部署", "发布"],
        "前端": ["frontend", "react", "vue", "angular", "html", "css", "javascript", "前端"],
        "后端": ["backend", "server", "api", "后端", "服务器"],
        "Python": ["python", "django", "flask", "fastapi", "pandas", "numpy", "gil"],
        "JavaScript": ["javascript", "typescript", "node", "nodejs", "react", "vue", "angular"],
        "Golang": ["go", "golang", "goroutine", "channel"],
        "AI/ML": ["ai", "ml", "machine learning", "deep learning", "模型", "训练", "神经网络"],
        "安全": ["security", "vulnerability", "攻击", "漏洞", "xss", "sql注入", "加密"],
        "测试": ["test", "testing", "unittest", "pytest", "jest", "测试", "单元测试", "集成测试"],
    }

    def __init__(
        self,
        similarity_threshold: float = 0.3,
        max_segment_messages: int = 10,
        max_segment_duration: timedelta = timedelta(minutes=30)
    ):
        self.similarity_threshold = similarity_threshold
        self.max_segment_messages = max_segment_messages
        self.max_segment_duration = max_segment_duration
        self.importance_scorer = ImportanceScorer()

    def segment(self, messages: List[Dict]) -> List[TopicSegment]:
        """
        将消息列表按主题分段

        Args:
            messages: [{id, content, created_at}, ...]

        Returns:
            List[TopicSegment]
        """
        if not messages:
            return []

        segments = []
        current_segment = self._create_new_segment(messages[0])

        for i in range(1, len(messages)):
            prev_msg = messages[i - 1]
            curr_msg = messages[i]

            should_split = self._should_split_segment(prev_msg, curr_msg, current_segment)

            if should_split:
                # 完成当前段
                current_segment.end_message_id = prev_msg["id"]
                segments.append(self._finalize_segment(current_segment, messages))
                # 开始新段
                current_segment = self._create_new_segment(curr_msg)
            else:
                # 继续当前段
                current_segment.message_count += 1
                current_segment.importance_score += self.importance_scorer.score(curr_msg["content"])

        # 完成最后一个段
        current_segment.end_message_id = messages[-1]["id"]
        segments.append(self._finalize_segment(current_segment, messages))

        return segments

    def _create_new_segment(self, first_message: Dict) -> TopicSegment:
        """创建新主题段"""
        content = first_message.get("content", "")
        topic_name = self._extract_topic_name(content)

        return TopicSegment(
            topic_name=topic_name,
            start_message_id=first_message["id"],
            end_message_id=first_message["id"],
            message_count=1,
            importance_score=self.importance_scorer.score(content),
            summary=""
        )

    def _finalize_segment(
        self,
        segment: TopicSegment,
        messages: List[Dict]
    ) -> TopicSegment:
        """完成主题段，生成摘要"""
        # 计算平均重要性
        if segment.message_count > 0:
            segment.importance_score = round(
                segment.importance_score / segment.message_count, 3
            )

        # 生成摘要
        segment.summary = self._generate_summary(segment, messages)

        return segment

    def _should_split_segment(
        self,
        prev_msg: Dict,
        curr_msg: Dict,
        current_segment: TopicSegment
    ) -> bool:
        """判断是否应该分割主题段"""
        # 1. 检查消息数限制
        if current_segment.message_count >= self.max_segment_messages:
            return True

        # 2. 检查时间间隔
        prev_time = prev_msg.get("created_at")
        curr_time = curr_msg.get("created_at")
        if prev_time and curr_time:
            if isinstance(curr_time, str):
                curr_time = datetime.fromisoformat(curr_time.replace('Z', '+00:00'))
            if isinstance(prev_time, str):
                prev_time = datetime.fromisoformat(prev_time.replace('Z', '+00:00'))

            time_diff = curr_time - prev_time
            if time_diff > self.max_segment_duration:
                return True

        # 3. 检查语义相似度
        similarity = self._calculate_similarity(
            prev_msg.get("content", ""),
            curr_msg.get("content", "")
        )
        if similarity < self.similarity_threshold:
            return True

        return False

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两段文本的语义相似度"""
        # 方法1: 关键词 Jaccard 相似度
        words1 = set(self._extract_keywords(text1))
        words2 = set(self._extract_keywords(text2))

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        jaccard_sim = intersection / union if union > 0 else 0.0

        # 方法2: 主题关键词重叠
        topic_sim = self._calculate_topic_similarity(text1, text2)

        # 综合相似度
        return max(jaccard_sim, topic_sim * 0.8)

    def _calculate_topic_similarity(self, text1: str, text2: str) -> float:
        """基于主题关键词的相似度"""
        text1_lower = text1.lower()
        text2_lower = text2.lower()

        # 获取每段文本匹配的主题
        topics1 = set()
        topics2 = set()

        for topic, keywords in self.TOPIC_KEYWORDS.items():
            if any(kw.lower() in text1_lower for kw in keywords):
                topics1.add(topic)
            if any(kw.lower() in text2_lower for kw in keywords):
                topics2.add(topic)

        if not topics1 or not topics2:
            return 0.0

        # 如果有共同主题，相似度较高
        common = len(topics1 & topics2)
        if common > 0:
            return 0.8 + 0.2 * (common / min(len(topics1), len(topics2)))

        return 0.0

    def _extract_keywords(self, text: str) -> List[str]:
        """提取文本关键词"""
        # 转换为小写
        text = text.lower()

        # 移除标点
        text = re.sub(r'[^\w\s]', ' ', text)

        # 分词
        words = text.split()

        # 过滤停用词和短词
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                     'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'could', 'should', 'may', 'might', 'must',
                     '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
                     '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
                     '你', '会', '着', '没有', '看', '好', '自己', '这'}

        keywords = [w for w in words if len(w) > 2 and w not in stopwords]

        return keywords

    def _extract_topic_name(self, content: str) -> str:
        """从内容中提取主题名称"""
        content_lower = content.lower()

        # 检查匹配的主题关键词
        topic_scores = {}
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in content_lower)
            if score > 0:
                topic_scores[topic] = score

        if topic_scores:
            # 返回匹配度最高的主题
            return max(topic_scores.items(), key=lambda x: x[1])[0]

        # 清理常见的引导词
        content_clean = content.strip()
        prefixes = ['让我们', '我们', '大家', '请', '来', '讨论', '谈谈', '聊聊', '说说', '看看', '关于']
        for prefix in prefixes:
            if content_clean.startswith(prefix):
                content_clean = content_clean[len(prefix):].strip()

        # 提取第一个短语
        match = re.search(r'^([^，。？！；,!?;]+)', content_clean)
        if match:
            topic = match.group(1).strip()
            if len(topic) >= 3:
                return topic[:25]

        # 如果内容很短，直接返回
        if len(content_clean) <= 25:
            return content_clean

        # 回退到关键词
        keywords = self._extract_keywords(content)
        if keywords:
            return keywords[0].capitalize()[:25]

        return content_clean[:25] if content_clean else "未命名主题"

    def _generate_summary(self, segment: TopicSegment, messages: List[Dict]) -> str:
        """为主题段生成摘要"""
        # 获取段内的所有消息内容
        segment_messages = [
            msg for msg in messages
            if segment.start_message_id <= msg["id"] <= segment.end_message_id
        ]

        if not segment_messages:
            return ""

        # 提取所有内容
        contents = [msg.get("content", "") for msg in segment_messages]

        # 简单摘要：第一句 + 关键句
        first_sentence = contents[0][:100]

        # 找包含关键词的重要句子
        important_sentences = []
        for content in contents:
            score = self.importance_scorer.score(content)
            if score > 0.7:
                important_sentences.append(content[:80])

        if important_sentences:
            summary = f"{first_sentence}... 关键点: {'; '.join(important_sentences[:2])}"
        else:
            summary = first_sentence[:150]

        return summary
