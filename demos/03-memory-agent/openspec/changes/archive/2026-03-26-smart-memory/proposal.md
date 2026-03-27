## Why

当前的长短记忆分层功能仅基于消息数量（每5条）触发摘要生成，缺乏对消息内容重要性的判断。这导致生成的摘要可能包含大量无关信息，而忽略了关键对话要点。

智能记忆功能将引入语义理解能力，自动识别重要对话节点，生成更高质量的上下文摘要，提升 AI 助手的长对话理解能力。

## What Changes

### 核心功能

1. **语义重要性评分（Importance Scoring）**
   - 使用 LLM 评估每条消息的重要性得分（0-1）
   - 评估维度：信息密度、决策相关度、用户强调程度、时间敏感性
   - 低重要性消息跳过详细处理，减少噪音

2. **自适应摘要触发（Adaptive Triggering）**
   - 替换固定"每5条触发"机制
   - 基于累积重要性得分触发摘要生成
   - 用户主动标记重要内容时立即触发

3. **主题分段（Topic Segmentation）**
   - 自动检测对话主题切换
   - 每个主题独立存储为 memory_segment
   - 主题内保持完整上下文，主题间通过摘要关联

4. **语义检索（Semantic Retrieval）**
   - 使用 pgvector 存储消息和摘要的向量表示
   - 用户提问时，自动检索相关历史记忆
   - 检索结果作为上下文补充给 LLM

### 技术实现

- 新增 `ImportanceScorer` 重要性评估器
- 新增 `TopicSegmenter` 主题检测器
- 新增 `VectorStore` pgvector 向量存储封装
- 重构 `SmartMemoryManager` 统一记忆管理入口

## Architecture

### 数据模型

```sql
-- messages 表扩展字段
ALTER TABLE messages ADD COLUMN importance_score FLOAT DEFAULT 0.5;
ALTER TABLE messages ADD COLUMN topic_tag VARCHAR(100);
ALTER TABLE messages ADD COLUMN embedding VECTOR(1536); -- 使用 pgvector

-- memory_segments 主题分段表
CREATE TABLE memory_segments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id),
    topic_name VARCHAR(200),
    start_message_id UUID REFERENCES messages(id),
    end_message_id UUID REFERENCES messages(id),
    summary_content TEXT,
    importance_score FLOAT DEFAULT 0.0,
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 向量索引
CREATE INDEX idx_messages_embedding ON messages USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_segments_embedding ON memory_segments USING ivfflat (embedding vector_cosine_ops);
```

### 核心组件

```python
class ImportanceScorer:
    """评估单条消息的重要性得分"""
    async def score(self, message: ChatMessage, context: List[ChatMessage]) -> float:
        # 返回 0-1 的重要性得分

class TopicSegmenter:
    """检测主题切换，进行分段"""
    async def detect_segment_boundary(self, messages: List[Message]) -> Optional[int]:
        # 判断是否开启新主题
    async def generate_segment_summary(self, segment_messages: List[Message]) -> str:

class VectorStore:
    """pgvector 向量存储封装"""
    async def store(self, content: str, metadata: Dict) -> None:
    async def search(self, query: str, top_k: int = 3) -> List[SearchResult]:
        # 语义相似度搜索

class SmartMemoryManager:
    """统一记忆管理入口"""
    async def process_new_message(self, session_id: str, message: Message):
        # 1. 评估重要性
        # 2. 检测主题切换
        # 3. 更新当前段摘要
        # 4. 向量存储
    async def get_context(self, session_id: str, current_query: str) -> List[Dict]:
        # 返回：当前主题摘要 + 语义检索结果 + 最近消息
```

### 消息处理流程

```
新消息到达
    ↓
评估重要性得分
    ↓
检测主题切换？
    ├── 是 → 创建新 memory_segment
    └── 否 → 继续当前 segment
    ↓
更新 segment 摘要
    ↓
存储向量表示（重要消息 + 摘要）
    ↓
完成
```

## Capabilities

### New Capabilities
- `semantic-memory`: 基于语义理解的智能记忆系统，包含重要性评分、自适应触发、主题分段等功能
- `memory-retrieval`: 记忆检索功能，支持语义相似度搜索
- `vector-storage`: pgvector 向量存储支持

### Modified Capabilities
- `memory-manager`: 重构为 SmartMemoryManager，整合所有智能记忆功能

## Development Methodology

### TDD 规范执行

本项目严格遵循 **测试驱动开发（TDD）** 规范：

- **RED**：先编写测试，描述预期行为，确认测试失败
- **GREEN**：编写最小实现使测试通过
- **REFACTOR**：重构代码，保持测试通过
- **VERIFY**：运行所有测试，确保覆盖率达标

**开发原则**：
- 所有代码修改必须先写测试
- 禁止未经测试直接实现功能
- 每个 public 方法必须有对应的单元测试
- 集成测试覆盖主要用户场景

## Success Criteria

### 功能验收标准

1. **重要性评分准确**：重要消息得分 > 0.7，闲聊消息得分 < 0.3
2. **主题分段准确**：同一主题内消息主题相似度 > 0.8
3. **检索召回率**：相关问题能召回 80% 以上的相关历史记忆
4. **响应延迟**：整体处理延迟增加 < 200ms

### 质量验收标准

5. **测试覆盖率**：单元测试覆盖率 **≥ 80%**
6. **测试通过率**：所有测试必须 100% 通过
7. **代码质量**：通过 Code Review，无 Critical/High 级别问题

## Impact

- **后端**：
  - 新增 `app/memory/importance.py` - 重要性评估
  - 新增 `app/memory/segmentation.py` - 主题分段
  - 新增 `app/memory/vector_store.py` - 向量存储
  - 重构 `app/memory/manager.py` - SmartMemoryManager

- **数据库**：
  - messages 表新增字段（importance_score, topic_tag, embedding）
  - 新增 memory_segments 表
  - 安装 pgvector 扩展

- **API**：
  - 聊天 API 集成智能记忆逻辑
  - 可能新增记忆检索测试接口

- **依赖**：
  - pgvector PostgreSQL 扩展
  - 向量嵌入模型（使用现有 LLM 或轻量级模型）

## Non-goals

- 多模态记忆（图片、音频）不在本次范围
- 跨会话记忆共享不在本次范围
- 用户手动编辑记忆功能不在本次范围
- 记忆持久化到外部存储（如 S3）不在本次范围
