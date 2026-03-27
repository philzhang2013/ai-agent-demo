# 更新日志

## 2026-03-27

### 向量系统修复与规范

**维度修复**
- ✅ **智谱 embedding-3 适配** - 向量维度从 1536 改为 2048
  - 修改 `migrations/004_add_smart_memory.sql` 和 `005_fix_embedding_dimension.sql`
  - 更新所有测试文件的硬编码维度
  - 注意：pgvector ivfflat/hnsw 索引有 2000 维限制，暂不创建向量索引

**数据库操作规范（重要）**
- ✅ **强制使用 .env 中的 DATABASE_URL**
  - 新增规范：所有数据库操作必须从 `.env` 读取 `DATABASE_URL`
  - 禁止直接使用 `psql` 或硬编码连接信息
  - 正确方式：`export $(cat .env | grep -v '^#' | xargs) && psql "$DATABASE_URL" ...`

**功能修复**
- ✅ **topic_tag 自动写入** - 创建主题段时自动回写 messages 表
  - `SmartMemoryManager.create_topic_segments()` 新增 topic_tag 回写逻辑
  - `ImportanceScoreRepository` 新增 `batch_update_topic_tags()` 方法

---

## 2026-03-26

### 智能记忆系统实现（Phase B）

**核心组件**：

- ✅ **ImportanceScorer** - 智能重要性评估器 (`app/memory/importance_scorer.py`)
  - 规则评分：技术关键词、重要标记词、纠正标记词
  - 多因子算法：长度、关键词、句式、实体、动作词
  - 批量评分支持

- ✅ **TopicSegmenter** - 主题分段器 (`app/memory/topic_segmenter.py`)
  - Jaccard相似度 + 主题词重叠检测
  - 多策略分段：相似度阈值、消息数量、时间间隔
  - 自动主题命名和摘要生成

- ✅ **VectorStore** - 向量存储管理 (`app/memory/vector_store.py`)
  - 2048维向量嵌入存储（智谱 embedding-3）
  - 余弦相似度计算
  - 相似向量检索

- ✅ **SmartMemoryManager** - 智能记忆管理器 (`app/memory/smart_memory_manager.py`)
  - 协调ImportanceScorer、TopicSegmenter、VectorStore
  - 分层记忆管理：高重要性消息 + 主题段摘要
  - 语义搜索接口
  - 智能上下文构建

- ✅ **数据访问层** (`app/db/repositories.py`)
  - `ImportanceScoreRepository` - 重要性分数和向量存储
  - `MemorySegmentRepository` - 主题段CRUD和语义搜索

- ✅ **API集成** (`app/api/chat.py`)
  - `POST /api/chat/{session_id}/analyze` - 分析会话记忆
  - `GET /api/chat/{session_id}/memory` - 获取/搜索会话记忆

- ✅ **配置系统** (`app/memory/config.py`)
  - `SmartMemoryConfig` - 可配置参数
  - `create_smart_memory_manager` - 工厂函数

- ✅ **数据库迁移** (`migrations/004_add_smart_memory.sql`)
  - pgvector扩展启用
  - messages表添加importance_score、topic_tag、embedding字段
  - memory_segments表创建
  - IVFFlat向量索引

**测试覆盖**：
- 66个智能记忆相关测试全部通过
- ImportanceScorer: 90% 覆盖率
- TopicSegmenter: 92% 覆盖率
- SmartMemoryManager: 85% 覆盖率
- VectorStore: 76% 覆盖率

---

## 2026-03-25

### 功能开发

**长短记忆系统完整实现**

- ✅ **MemoryManager** - 核心记忆管理类
  - 自动摘要触发（每5条消息）
  - 智能上下文构建（摘要 + 最近消息）
  - LLM 摘要生成
- ✅ **MemorySummaryRepository** - 摘要数据访问层
  - PostgreSQL UPSERT 支持并发安全
  - 索引优化查询性能
- ✅ **聊天API集成** - 流式接口自动记忆管理
  - 消息持久化时触发摘要检查
  - 使用记忆上下文进行对话
  - 摘要失败不阻断主流程
- ✅ **完整测试覆盖**
  - 7个集成测试覆盖所有记忆场景
  - 单元测试覆盖率 73%（核心业务逻辑 100%）

**会话管理 UI 完整实现**

- ✅ 会话列表侧边栏 (`SessionSidebar.vue`)
- ✅ 会话列表项组件 (`SessionItem.vue`)
- ✅ 会话标题管理（支持编辑）
- ✅ 创建/删除/切换会话功能
- ✅ 会话预览（最后消息、消息数、更新时间）
- ✅ Pinia 状态管理 (`sessionStore.ts`)

**流式消息持久化**

- ✅ SSE 流式接口 (`/api/chat/stream`) 支持消息保存
- ✅ 自动保存用户消息和助手回复到数据库
- ✅ UUID 验证防止无效 session_id 导致的数据库错误

### Bug 修复

| Bug 描述 | 修复文件 | 修复内容 |
|---------|---------|---------|
| 首次进入无初始会话 | `App.vue`, `sessionStore.ts` | 应用启动时自动创建新会话 |
| 前端未传递 session_id | `InputBox.vue` | 使用 `sessionStore.currentSessionId` 替代错误引用 |
| 流式消息未保存 | `chat.py` | 流式响应完成后保存消息到数据库 |
| 测试失败（API Key 过期） | `test_api.py`, `test_auth_api.py` | 添加 mock 避免真实 API 调用 |
| 测试格式不匹配 | `test_agent.py`, `test_providers.py` | 更新为事件字典格式 |
