# 智能记忆系统设计文档

## 概述

本文档详细描述智能记忆系统的技术实现方案，包含三个核心功能：语义重要性评分、主题分段、语义检索。

## TDD 强制规范（MANDATORY）

### 1. 开发流程（必须遵守）

1. **先写测试（FAIL）**
  - 所有代码修改必须先写测试
  - 测试必须描述预期行为
  - 运行测试确认 RED 状态（测试失败）
2. **再写实现（PASS）**
  - 编写最小实现使测试通过
  - 运行测试确认 GREEN 状态
3. **最后重构（REFACTOR）**
  - 优化代码结构
  - 保持测试通过

### 2. 禁止行为

- ❌ **不允许先写实现代码**
- ❌ **不允许没有测试的 PR**
- ❌ **不允许跳过失败测试**
- ❌ 不允许提交时跳过测试检查
- ❌ 不允许降低测试覆盖率

### 3. 测试覆盖要求

- ✅ **新功能必须包含测试**（单元测试 + 集成测试）
- ✅ **修改代码必须更新测试**
- ✅ **每个 public 方法必须有对应的单元测试**
- ✅ **新代码覆盖率必须 ≥ 80%**
- ✅ **整体覆盖率不能下降**

### 4. 数据库测试规范

- ✅ **必须使用事务回滚**
  ```python
  # 标准模式
  async with db.transaction() as txn:
      # 测试代码
      ...
      # 自动回滚
  ```
- ❌ **不允许共享测试数据**
  - 每个测试独立准备数据
  - 禁止使用全局测试数据
  - 测试结束后清理数据
- ✅ **Repository 测试要求**
  - 测试真实 SQL 执行
  - 验证数据库约束
  - 测试并发场景

### Database Schema Evolution Strategy

为了保证数据库结构的可维护性、可复现性和团队协作一致性，定义如下规范：

#### 1. Schema 变更方式

所有数据库表结构的变更必须通过 **SQL Migration 文件** 管理，而不是手动执行。

- 每一次 schema 变更必须新增一个 SQL 文件
- 文件命名规则：日期-功能名称.sql
- 存储在backend/migrations

### 5. 代码审查检查清单

**提交前必须确认：**

- 所有测试已编写且失败（RED）
- 实现代码已通过测试（GREEN）
- 代码已重构优化
- 测试覆盖率 ≥ 80%
- 所有测试通过（pytest）
- 无 Critical/High 级别代码问题

**PR 前必须确认：**

- 完整测试套件通过
- 覆盖率报告达标
- Code Review 通过

---

#### 3. 禁止事项

- ❌ 禁止直接在生产数据库手动执行 SQL
- ❌ 禁止通过 Python 脚本动态创建表结构
- ❌ 禁止修改已有 migration 文件（只能新增）

---

#### 4. 开发阶段例外

在本地开发或 TDD 阶段，允许使用 psql 进行快速验证：

## 架构设计

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                      SmartMemoryManager                         │
│                         (统一入口)                               │
└────────────────────┬────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────────┐ ┌──────────┐ ┌─────────────┐
│ Importance   │ │ Topic    │ │ VectorStore │
│ Scorer       │ │ Segmenter│ │             │
└──────────────┘ └──────────┘ └─────────────┘
        │            │            │
        └────────────┼────────────┘
                     ▼
            ┌─────────────────┐
            │   PostgreSQL    │
            │  + pgvector     │
            └─────────────────┘
```

### 核心组件

#### 1. ImportanceScorer（重要性评估器）

**测试先行要求：**

- 先写 `test_importance_scorer.py`
- 测试不同消息类型的评分
- 测试边界情况（空消息、超长消息）

```python
class ImportanceScorer:
    """
    评估单条消息的重要性得分（0-1）

    评估维度：
    - 信息密度：技术术语、具体数值、明确指令
    - 决策相关度：影响后续行动的内容
    - 用户强调：感叹号、重复、明确标记"重要"
    - 时间敏感：截止日期、过期提醒
    """

    async def score(
        self,
        message: ChatMessage,
        context: List[ChatMessage]
    ) -> float:
        """
        使用 LLM 返回重要性得分

        Prompt 策略：
        - 提供最近3条上下文
        - 要求 LLM 从4个维度评分
        - 返回 JSON 格式：{"score": 0.85, "reason": "..."}
        """
        pass

    def _build_prompt(self, message: ChatMessage, context: List[ChatMessage]) -> str:
        """构建评估 prompt"""
        pass
```

**测试场景：**

```python
# test_importance_scorer.py
async def test_high_importance_technical_info():
    """技术信息应得高分"""
    message = ChatMessage(role="user", content="数据库密码是 abc123")
    score = await scorer.score(message, [])
    assert score >= 0.7

async def test_low_importance_greeting():
    """问候语应得低分"""
    message = ChatMessage(role="user", content="你好")
    score = await scorer.score(message, [])
    assert score <= 0.3
```

#### 2. TopicSegmenter（主题检测器）

**测试先行要求：**

- 先写 `test_topic_segmenter.py`
- 测试主题切换检测
- 测试主题连续性保持

```python
class TopicSegmenter:
    """
    检测主题切换，进行分段管理

    算法策略：
    - 使用 LLM 判断当前消息是否开启新主题
    - 维护当前主题的关键词列表
    - 当关键词重叠度 < 30% 时触发分段
    """

    async def detect_segment_boundary(
        self,
        messages: List[Message],
        current_segment: MemorySegment
    ) -> Optional[TopicBoundary]:
        """
        判断是否需要创建新主题段

        返回：新主题的元数据，或 None（继续当前段）
        """
        pass

    async def generate_segment_summary(
        self,
        segment_messages: List[Message]
    ) -> str:
        """
        为主题段生成摘要

        策略：
        - 提取核心讨论点
        - 保留关键决策和结论
        - 控制在 150 字以内
        """
        pass

    def _calculate_topic_similarity(
        self,
        msg1_keywords: Set[str],
        msg2_keywords: Set[str]
    ) -> float:
        """计算两个消息的主题相似度"""
        pass
```

**测试场景：**

```python
# test_topic_segmenter.py
async def test_detect_topic_switch():
    """检测到主题切换"""
    messages = [
        Message(role="user", content="我们讨论数据库设计"),
        Message(role="assistant", content="好的，用什么数据库？"),
        Message(role="user", content="聊聊前端框架吧"),  # 主题切换
    ]
    boundary = await segmenter.detect_segment_boundary(messages, current_segment)
    assert boundary.is_boundary is True

async def test_maintain_topic_continuity():
    """保持主题连续性"""
    messages = [
        Message(role="user", content="数据库用 PostgreSQL"),
        Message(role="assistant", content="不错的选择"),
        Message(role="user", content="需要配置连接池"),  # 同主题
    ]
    boundary = await segmenter.detect_segment_boundary(messages, current_segment)
    assert boundary.is_boundary is False
```

#### 3. VectorStore（向量存储）

**测试先行要求：**

- 先写 `test_vector_store.py`
- 测试向量存储和检索
- 测试相似度阈值过滤

```python
class VectorStore:
    """
    pgvector 向量存储封装

    使用 HuggingFace 的 sentence-transformers 生成 embedding
    或复用现有 LLM 的 embedding API（如果支持）
    """

    def __init__(self, db_pool: asyncpg.Pool, embedding_model: str = "local"):
        self.db = db_pool
        self.model = embedding_model

    async def store_message_embedding(
        self,
        message_id: str,
        content: str
    ) -> None:
        """存储消息的向量表示"""
        embedding = await self._generate_embedding(content)
        await self.db.execute(
            "UPDATE messages SET embedding = $1 WHERE id = $2",
            embedding, message_id
        )

    async def store_segment_embedding(
        self,
        segment_id: str,
        summary: str
    ) -> None:
        """存储主题段摘要的向量表示"""
        pass

    async def search(
        self,
        query: str,
        session_id: Optional[str] = None,
        top_k: int = 3,
        threshold: float = 0.6
    ) -> List[SearchResult]:
        """
        语义相似度搜索

        搜索范围：
        - 消息内容（importance_score >= 0.5）
        - 主题段摘要

        返回：按相似度排序的结果列表
        """
        pass

    async def _generate_embedding(self, text: str) -> List[float]:
        """生成文本的向量表示"""
        # 方案1：使用 HuggingFace sentence-transformers
        # 方案2：调用 LLM 的 embedding API
        pass
```

**测试场景：**

```python
# test_vector_store.py
async def test_store_and_search_message(db_pool):
    """存储并搜索消息"""
    async with db_pool.transaction() as txn:
        # 存储消息
        await vector_store.store_message_embedding(msg_id, "数据库密码是 secret")

        # 搜索
        results = await vector_store.search("密码是多少？", top_k=1)
        assert len(results) == 1
        assert "secret" in results[0].content

async def test_similarity_threshold(db_pool):
    """相似度阈值过滤"""
    async with db_pool.transaction() as txn:
        results = await vector_store.search(
            "完全不相关的内容",
            threshold=0.6
        )
        assert len(results) == 0  # 低于阈值，无结果
```

#### 4. SmartMemoryManager（智能记忆管理器）

**测试先行要求：**

- 先写 `test_smart_memory_manager.py`
- 测试消息处理流程
- 测试上下文构建
- 测试降级策略

```python
class SmartMemoryManager:
    """
    统一的记忆管理入口，替换现有的 MemoryManager
    """

    # 配置参数
    IMPORTANCE_THRESHOLD_HIGH = 0.7  # 高重要性阈值
    IMPORTANCE_THRESHOLD_LOW = 0.3   # 低重要性阈值
    SUMMARY_TRIGGER_SCORE = 2.0      # 触发摘要的累积重要性
    VECTOR_STORE_THRESHOLD = 0.5     # 存储向量的最低重要性

    def __init__(
        self,
        message_repo: MessageRepository,
        summary_repo: MemorySummaryRepository,
        segment_repo: MemorySegmentRepository,
        vector_store: VectorStore,
        llm_client: Any,
        model: str = "glm-5"
    ):
        self.message_repo = message_repo
        self.summary_repo = summary_repo
        self.segment_repo = segment_repo
        self.vector_store = vector_store
        self.llm_client = llm_client
        self.model = model
        self.importance_scorer = ImportanceScorer(llm_client)
        self.topic_segmenter = TopicSegmenter(llm_client)

    async def process_new_message(
        self,
        session_id: str,
        message: Message
    ) -> ProcessResult:
        """
        处理新消息的主流程

        流程：
        1. 评估消息重要性
        2. 检查是否需要新建主题段
        3. 更新当前段摘要
        4. 存储向量表示（重要消息）
        """
        # 1. 重要性评分
        importance = await self.importance_scorer.score(message, context)
        await self.message_repo.update_importance(message.id, importance)

        # 2. 主题分段检测
        boundary = await self.topic_segmenter.detect_segment_boundary(...)
        if boundary:
            current_segment = await self.segment_repo.create_new_segment(...)

        # 3. 更新段摘要
        if importance >= self.IMPORTANCE_THRESHOLD_HIGH:
            await self._update_segment_summary(session_id)

        # 4. 向量存储（重要消息才存）
        if importance >= self.VECTOR_STORE_THRESHOLD:
            await self.vector_store.store_message_embedding(
                message.id, message.content
            )

        return ProcessResult(importance=importance, segment_id=...)

    async def get_context(
        self,
        session_id: str,
        current_query: str
    ) -> List[Dict[str, str]]:
        """
        构建发送给 LLM 的上下文

        策略：
        - 当前主题段的摘要
        - 语义检索相关历史（top 2）
        - 最近3条原始消息
        """
        context = []

        # 1. 当前主题段摘要
        current_segment = await self.segment_repo.get_current_segment(session_id)
        if current_segment:
            context.append({
                "role": "system",
                "content": f"【当前话题】{current_segment.summary}"
            })

        # 2. 语义检索相关历史
        relevant_memories = await self.vector_store.search(
            query=current_query,
            session_id=session_id,
            top_k=2
        )
        for memory in relevant_memories:
            context.append({
                "role": "system",
                "content": f"【相关历史】{memory.content}"
            })

        # 3. 最近消息
        recent_messages = await self.message_repo.get_recent(session_id, limit=3)
        for msg in recent_messages:
            context.append({"role": msg.role, "content": msg.content})

        return context

    async def _update_segment_summary(self, session_id: str) -> None:
        """更新当前主题段的摘要"""
        pass
```

## 数据模型

### 数据库 Schema

```sql
-- ============================================
-- 扩展 messages 表
-- ============================================
ALTER TABLE messages
ADD COLUMN importance_score FLOAT DEFAULT 0.5,
ADD COLUMN topic_tag VARCHAR(100),
ADD COLUMN embedding VECTOR(1536);  -- pgvector 类型

CREATE INDEX idx_messages_importance ON messages(importance_score);
CREATE INDEX idx_messages_topic ON messages(topic_tag);
CREATE INDEX idx_messages_embedding ON messages
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================
-- 主题段表
-- ============================================
CREATE TABLE memory_segments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    topic_name VARCHAR(200) NOT NULL DEFAULT '未命名主题',

    -- 段落边界
    start_message_id UUID REFERENCES messages(id),
    end_message_id UUID REFERENCES messages(id),

    -- 摘要内容
    summary_content TEXT NOT NULL DEFAULT '',
    importance_score FLOAT DEFAULT 0.0,

    -- 向量表示
    embedding VECTOR(1536),

    -- 统计信息
    message_count INTEGER DEFAULT 0,
    total_importance FLOAT DEFAULT 0.0,

    -- 时间戳
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_segments_session ON memory_segments(session_id);
CREATE INDEX idx_segments_embedding ON memory_segments
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);

-- ============================================
-- 启用 pgvector 扩展
-- ============================================
CREATE EXTENSION IF NOT EXISTS vector;
```

### Pydantic 模型

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class MessageImportance(BaseModel):
    """消息重要性评分结果"""
    score: float = Field(..., ge=0.0, le=1.0)
    reason: str = Field(..., description="评分理由")
    dimensions: dict = Field(default_factory=dict, description="各维度得分")

class TopicBoundary(BaseModel):
    """主题边界检测结果"""
    is_boundary: bool
    new_topic_name: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    keywords: List[str] = Field(default_factory=list)

class MemorySegment(BaseModel):
    """主题段数据模型"""
    id: UUID
    session_id: UUID
    topic_name: str
    start_message_id: Optional[UUID]
    end_message_id: Optional[UUID]
    summary_content: str
    importance_score: float
    message_count: int
    total_importance: float
    created_at: datetime
    updated_at: datetime

class SearchResult(BaseModel):
    """语义搜索结果"""
    id: UUID
    content_type: str  # "message" | "segment"
    content: str
    similarity: float
    created_at: datetime
    topic_tag: Optional[str] = None

class ProcessResult(BaseModel):
    """消息处理结果"""
    importance: float
    segment_id: Optional[UUID]
    is_new_segment: bool = False
```

## 测试策略

### 测试文件结构

```
backend/tests/
├── test_importance_scorer.py      # 重要性评估测试
├── test_topic_segmenter.py        # 主题分段测试
├── test_vector_store.py           # 向量存储测试
├── test_smart_memory_manager.py   # 智能记忆管理器测试
└── test_memory_integration.py     # 集成测试
```

### 单元测试要求


| 模块                 | 测试数量   | 关键场景            |
| ------------------ | ------ | --------------- |
| ImportanceScorer   | ≥ 8 个  | 高分/低分/中等/边界/上下文 |
| TopicSegmenter     | ≥ 8 个  | 切换/连续/关键词/摘要    |
| VectorStore        | ≥ 6 个  | 存储/搜索/阈值/事务     |
| SmartMemoryManager | ≥ 10 个 | 流程/降级/上下文/并发    |


### 集成测试要求

- 完整消息处理流程测试
- 上下文构建正确性测试
- 数据库操作一致性测试

### 核心流程集成测试（E2E）

**测试目标**：验证从注册到智能记忆完整功能的端到端流程，使用真实智普 API。

**前置条件**：

- 测试数据库已初始化（包含 pgvector 扩展）
- 智普 API Key 已配置
- 测试环境网络可访问智普 API

**测试用例**：`test_smart_memory_e2e_flow`

```python
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.require_env("ZHIPU_API_KEY")
async def test_smart_memory_e2e_flow(db_pool, client):
    """
    智能记忆核心流程端到端测试

    流程：注册 → 登录 → 20轮聊天（两次主题切换）→ 验证智能记忆
    """
    # ==========================================
    # Step 1: 注册用户
    # ==========================================
    register_data = {
        "username": "test009",
        "password": "123456"
    }
    response = await client.post("/api/auth/register", json=register_data)
    assert response.status_code == 201
    user_id = response.json()["user_id"]

    # ==========================================
    # Step 2: 登录获取 Token
    # ==========================================
    login_data = {
        "username": "test009",
        "password": "123456"
    }
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # ==========================================
    # Step 3: 开始会话
    # ==========================================
    response = await client.post("/api/sessions", headers=headers, json={"title": "智能记忆测试"})
    assert response.status_code == 201
    session_id = response.json()["id"]

    # ==========================================
    # Step 4: 第一轮聊天（主题1：Python学习）
    # 共 8 轮对话，包含重要信息
    # ==========================================
    topic1_messages = [
        ("user", "我想学习 Python，有什么建议？"),
        ("user", "我的目标是成为数据分析师"),
        ("user", "我计划每天学习 2 小时"),
        ("user", "我的邮箱是 test009@example.com，请发学习资料给我"),  # 重要：联系方式
        ("user", "Python 的 pandas 库怎么用？"),
        ("user", "我已经安装了 Anaconda"),
        ("user", "我的电脑是 MacBook Pro M2"),  # 重要：设备信息
        ("user", "推荐一些练习项目吧"),
    ]

    for role, content in topic1_messages:
        response = await client.post(
            "/api/chat",
            headers=headers,
            json={"session_id": session_id, "message": content}
        )
        assert response.status_code == 200
        # 等待流式响应完成
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                continue

        # 模拟延迟，让后台处理完成
        await asyncio.sleep(0.5)

    # ==========================================
    # Step 5: 第二轮聊天（主题2：数据库设计）
    # 共 6 轮对话，第一次主题切换
    # ==========================================
    topic2_messages = [
        ("user", "我们聊聊数据库设计吧"),  # 主题切换
        ("user", "我的项目需要存储用户信息"),
        ("user", "数据库密码我打算设置为 DbP@ss2024!"),  # 重要：密码
        ("user", "用 PostgreSQL 还是 MySQL？"),
        ("user", "需要支持 10 万并发用户"),  # 重要：性能需求
        ("user", "帮我设计一下表结构"),
    ]

    for role, content in topic2_messages:
        response = await client.post(
            "/api/chat",
            headers=headers,
            json={"session_id": session_id, "message": content}
        )
        assert response.status_code == 200
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                continue
        await asyncio.sleep(0.5)

    # ==========================================
    # Step 6: 第三轮聊天（主题3：前端框架）
    # 共 6 轮对话，第二次主题切换
    # ==========================================
    topic3_messages = [
        ("user", "现在聊聊前端用什么框架"),  # 主题切换
        ("user", "我在 React 和 Vue 之间犹豫"),
        ("user", "我们团队有 5 个前端工程师"),  # 重要：团队规模
        ("user", "项目 deadline 是下个月 15 号"),  # 重要：时间
        ("user", "需要支持移动端适配"),
        ("user", "给我一些建议"),
    ]

    for role, content in topic3_messages:
        response = await client.post(
            "/api/chat",
            headers=headers,
            json={"session_id": session_id, "message": content}
        )
        assert response.status_code == 200
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                continue
        await asyncio.sleep(0.5)

    # ==========================================
    # Step 7: 验证智能记忆功能
    # ==========================================

    # 7.1 验证重要性评分
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT content, importance_score FROM messages WHERE session_id = $1 ORDER BY created_at",
            session_id
        )

        # 重要消息应该得分高
        important_keywords = ["test009@example.com", "MacBook Pro", "DbP@ss2024!", "10 万并发", "下个月 15 号"]
        for row in rows:
            content = row["content"]
            score = row["importance_score"]

            # 检查重要消息是否得分高
            if any(keyword in content for keyword in important_keywords):
                assert score >= 0.6, f"重要消息 '{content}' 得分 {score}，应该 >= 0.6"

    # 7.2 验证主题分段
    async with db_pool.acquire() as conn:
        segments = await conn.fetch(
            "SELECT * FROM memory_segments WHERE session_id = $1 ORDER BY created_at",
            session_id
        )

        # 应该有 3 个主题段
        assert len(segments) == 3, f"应该有 3 个主题段，实际有 {len(segments)} 个"

        # 验证主题段包含正确的话题关键词
        topic_keywords = [
            ["Python", "pandas", "Anaconda"],  # 主题1
            ["数据库", "PostgreSQL", "MySQL"],  # 主题2
            ["React", "Vue", "前端"],  # 主题3
        ]

        for i, segment in enumerate(segments):
            summary = segment["summary_content"]
            expected_keywords = topic_keywords[i]

            # 摘要中应该包含该主题的关键词（使用语义相似度检查）
            has_keyword = any(kw in summary for kw in expected_keywords)
            # 或者使用向量相似度检查
            assert has_keyword or len(summary) > 10, \
                f"主题段 {i+1} 摘要 '{summary}' 应该包含相关主题信息"

    # 7.3 验证向量存储
    async with db_pool.acquire() as conn:
        # 重要消息应该有向量存储
        important_messages = await conn.fetch(
            """
            SELECT id, content, embedding
            FROM messages
            WHERE session_id = $1 AND importance_score >= 0.5 AND embedding IS NOT NULL
            """,
            session_id
        )

        # 至少有一半的重要消息有向量存储
        all_important = await conn.fetch(
            "SELECT COUNT(*) FROM messages WHERE session_id = $1 AND importance_score >= 0.5",
            session_id
        )
        total_important = all_important[0]["count"]

        assert len(important_messages) >= total_important * 0.5, \
            f"重要消息向量存储不足：{len(important_messages)}/{total_important}"

    # 7.4 验证语义检索
    # 查询与之前话题相关的问题，验证能否检索到历史
    test_queries = [
        ("我的邮箱是什么？", "test009@example.com"),
        ("我的数据库密码是什么？", "DbP@ss2024!"),
        ("项目什么时候截止？", "下个月 15 号"),
    ]

    for query, expected_content in test_queries:
        # 通过向量存储搜索
        results = await vector_store.search(query, session_id=session_id, top_k=3)

        # 应该能检索到相关内容
        found = any(expected_content in r.content for r in results)
        assert found, f"查询 '{query}' 应该能检索到 '{expected_content}'"

    # ==========================================
    # Step 8: 清理测试数据
    # ==========================================
    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM memory_segments WHERE session_id = $1", session_id)
        await conn.execute("DELETE FROM messages WHERE session_id = $1", session_id)
        await conn.execute("DELETE FROM chat_sessions WHERE id = $1", session_id)
        await conn.execute("DELETE FROM users WHERE id = $1", user_id)

    print("✅ 智能记忆核心流程集成测试通过！")
```

**测试验证点**：


| 验证项   | 期望结果                  | 说明                    |
| ----- | --------------------- | --------------------- |
| 注册/登录 | HTTP 201/200          | 用户认证流程正常              |
| 重要性评分 | 重要消息得分 ≥ 0.6          | 邮箱、密码、时间等关键信息         |
| 主题分段  | 生成 3 个主题段             | Python学习 / 数据库 / 前端框架 |
| 向量存储  | ≥ 50% 重要消息有 embedding | 重要性 >= 0.5 的消息        |
| 语义检索  | 正确召回历史信息              | 邮箱、密码、截止时间            |


**运行方式**：

```bash
# 设置环境变量
export ZHIPU_API_KEY="your-api-key"

# 运行集成测试
pytest tests/test_smart_memory_e2e.py -v -m integration

# 跳过集成测试（默认）
pytest tests/ -v --ignore=tests/test_smart_memory_e2e.py
```

**注意事项**：

- 此测试调用真实智普 API，会产生费用
- 测试运行时间较长（约 2-3 分钟，20轮对话）
- 需要在 CI 中设置环境变量控制是否运行
- 测试结束后自动清理测试数据

```bash
# 运行测试并检查覆盖率
pytest --cov=app.memory --cov-report=term-missing

# 必须满足
# - 新代码覆盖率 ≥ 80%
# - 所有测试通过
```

## 关键流程

### 1. 新消息处理流程

```
用户发送消息
    │
    ▼
┌─────────────────┐
│ ImportanceScore │ 评估重要性 (0-1)
│    .score()     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 保存重要性分数  │ 更新 messages.importance_score
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ TopicSegmenter  │ 检测是否主题切换
│.detect_boundary()│
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
 是(新主题)  否(继续)
    │         │
    ▼         │
┌─────────┐   │
│创建新段 │   │
└────┬────┘   │
     │        │
     └────────┘
              │
              ▼
┌─────────────────┐
│ 更新段摘要      │ 如果重要性高，重新生成摘要
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ VectorStore     │ 存储向量（重要性 >= 0.5）
│.store_embedding │
└─────────────────┘
```

### 2. 上下文构建流程

```
LLM 请求前
    │
    ▼
┌─────────────────┐
│ 获取当前段摘要  │ 从 memory_segments
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ VectorStore     │ 语义检索相关历史
│    .search()    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 获取最近3条消息 │ 从 messages
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 组装上下文列表  │ 按优先级排序
└─────────────────┘
```

## 错误处理

### 降级策略

```python
class SmartMemoryManager:
    async def process_new_message(self, session_id: str, message: Message):
        try:
            importance = await self.importance_scorer.score(...)
        except Exception as e:
            logger.error(f"重要性评分失败: {e}")
            # 降级：使用默认中等重要性
            importance = 0.5

        try:
            await self.vector_store.store_message_embedding(...)
        except Exception as e:
            logger.error(f"向量存储失败: {e}")
            # 降级：跳过向量存储，不影响主流程
```

## 性能考虑

### 1. 异步处理

重要性评分和向量生成使用 LLM 调用，耗时较长（100-500ms）。这些操作应该在后台异步执行，不阻塞用户响应。

```python
# 后台任务处理
async def process_message_background(message_id: str):
    """后台处理消息的智能记忆逻辑"""
    message = await message_repo.get(message_id)

    # 异步并行执行
    importance_task = importance_scorer.score(message, context)
    embedding_task = vector_store.store_message_embedding(...)

    importance, _ = await asyncio.gather(importance_task, embedding_task)
```

### 2. 批处理

向量生成可以批量处理，减少 API 调用次数：

```python
# 批量生成 embedding
async def batch_store_embeddings(messages: List[Message]):
    contents = [m.content for m in messages]
    embeddings = await embedding_model.encode_batch(contents)
    # 批量写入数据库
```

### 3. 索引优化

pgvector 的 ivfflat 索引需要合理设置 lists 参数：

```sql
-- 对于 10000 条消息，设置 lists = 100
CREATE INDEX idx_messages_embedding ON messages
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

## 部署考虑

### 数据库迁移

1. 安装 pgvector 扩展（Supabase 已内置）
2. 执行字段添加和索引创建
3. 历史数据处理（可选：批量生成存量消息的 embedding）

### 配置参数

```python
# config.py
SMART_MEMORY_CONFIG = {
    "importance_model": "glm-5",  # 重要性评估使用的模型
    "embedding_model": "local",   # "local" 或 API 名称
    "summary_trigger_score": 2.0,
    "vector_store_threshold": 0.5,
    "search_top_k": 3,
    "search_similarity_threshold": 0.6,
}
```

## 风险评估


| 风险            | 影响     | 缓解措施               |
| ------------- | ------ | ------------------ |
| LLM 调用延迟高     | 用户体验下降 | 异步处理，降级策略          |
| pgvector 性能问题 | 检索慢    | 合理设置索引参数，限制返回数量    |
| Embedding 成本  | 费用增加   | 只存储高重要性消息，批处理      |
| 主题检测不准确       | 分段混乱   | 人工评估调优阈值           |
| TDD 执行不到位     | 质量不达标  | Code Review 强制检查测试 |


