# 智能记忆功能实现任务列表

## Phase 1: 数据库与 Repository（TDD）

### Task 1.1: 创建数据库迁移脚本
**类型**: chore
**文件**: `backend/migrations/004_add_smart_memory.sql`

- [ ] 1.1.1 编写测试：验证迁移后表结构正确
- [ ] 1.1.2 启用 pgvector 扩展：`CREATE EXTENSION IF NOT EXISTS vector`
- [ ] 1.1.3 messages 表新增字段：importance_score, topic_tag, embedding
- [ ] 1.1.4 创建 memory_segments 表
- [ ] 1.1.5 创建向量索引：idx_messages_embedding, idx_segments_embedding
- [ ] 1.1.6 运行测试确认通过

**验收**: 迁移脚本可正常执行，所有测试通过 ✅

---

### Task 1.2: 创建 MemorySegmentRepository 测试
**类型**: test
**文件**: `backend/tests/test_memory_segment_repository.py`

- [ ] 1.2.1 RED: 编写 `test_create_segment_success` - 正常创建主题段
- [ ] 1.2.2 RED: 编写 `test_find_by_session_id` - 按会话查找
- [ ] 1.2.3 RED: 编写 `test_get_current_segment` - 获取当前主题段
- [ ] 1.2.4 RED: 编写 `test_update_summary` - 更新段摘要
- [ ] 1.2.5 RED: 编写 `test_find_segments_by_session_ordered` - 按时间排序
- [ ] 1.2.6 运行测试确认全部失败

**验收**: 5个测试全部失败（RED 状态）✅

---

### Task 1.3: 实现 MemorySegmentRepository
**类型**: feat
**文件**: `backend/app/db/repositories.py`

- [ ] 1.3.1 GREEN: 实现 `MemorySegmentRepository` 类
- [ ] 1.3.2 GREEN: 实现 `create()` 方法
- [ ] 1.3.3 GREEN: 实现 `find_by_session_id()` 方法
- [ ] 1.3.4 GREEN: 实现 `get_current_segment()` 方法
- [ ] 1.3.5 GREEN: 实现 `update_summary()` 方法
- [ ] 1.3.6 运行测试确认全部通过

**验收**: Task 1.2 的5个测试全部通过（GREEN 状态）✅

---

### Task 1.4: 扩展 MessageRepository
**类型**: feat
**文件**: `backend/app/db/repositories.py`

- [ ] 1.4.1 RED: 编写 `test_update_importance` 测试
- [ ] 1.4.2 RED: 编写 `test_update_topic_tag` 测试
- [ ] 1.4.3 RED: 编写 `test_get_recent_messages` 测试
- [ ] 1.4.4 RED: 编写 `test_get_unprocessed_messages` 测试
- [ ] 1.4.5 GREEN: 实现 `update_importance()` 方法
- [ ] 1.4.6 GREEN: 实现 `update_topic_tag()` 方法
- [ ] 1.4.7 GREEN: 实现 `get_recent()` 方法
- [ ] 1.4.8 GREEN: 实现 `get_unprocessed()` 方法
- [ ] 1.4.9 运行测试确认全部通过

**验收**: 所有扩展方法测试通过 ✅

---

**Phase 1 状态: ⬜ 待开始**

---

## Phase 2: 核心组件实现（TDD）

### Task 2.1: ImportanceScorer 重要性评估器
**类型**: feat
**文件**: `backend/app/memory/importance.py`, `backend/tests/test_importance_scorer.py`

- [ ] 2.1.1 RED: 编写 `test_high_importance_technical_info` - 技术信息高分
- [ ] 2.1.2 RED: 编写 `test_low_importance_greeting` - 问候语低分
- [ ] 2.1.3 RED: 编写 `test_medium_importance_question` - 一般问题中等分
- [ ] 2.1.4 RED: 编写 `test_importance_with_context` - 带上下文评估
- [ ] 2.1.5 RED: 编写 `test_empty_message_handling` - 空消息处理
- [ ] 2.1.6 GREEN: 实现 `ImportanceScorer` 类
- [ ] 2.1.7 GREEN: 实现 `score()` 方法
- [ ] 2.1.8 GREEN: 实现 `_build_prompt()` 方法
- [ ] 2.1.9 REFACTOR: 优化 prompt 模板和解析逻辑
- [ ] 2.1.10 VERIFY: 运行测试，覆盖率 ≥ 80%

**验收**: 5个测试全部通过，覆盖率达标 ✅

---

### Task 2.2: TopicSegmenter 主题检测器
**类型**: feat
**文件**: `backend/app/memory/segmentation.py`, `backend/tests/test_topic_segmenter.py`

- [ ] 2.2.1 RED: 编写 `test_detect_topic_switch` - 检测主题切换
- [ ] 2.2.2 RED: 编写 `test_maintain_topic_continuity` - 保持主题连续
- [ ] 2.2.3 RED: 编写 `test_generate_segment_summary` - 生成段摘要
- [ ] 2.2.4 RED: 编写 `test_keyword_extraction` - 关键词提取
- [ ] 2.2.5 RED: 编写 `test_topic_similarity_calculation` - 相似度计算
- [ ] 2.2.6 GREEN: 实现 `TopicSegmenter` 类
- [ ] 2.2.7 GREEN: 实现 `detect_segment_boundary()` 方法
- [ ] 2.2.8 GREEN: 实现 `generate_segment_summary()` 方法
- [ ] 2.2.9 GREEN: 实现 `_calculate_topic_similarity()` 方法
- [ ] 2.2.10 REFACTOR: 优化主题检测算法
- [ ] 2.2.11 VERIFY: 运行测试，覆盖率 ≥ 80%

**验收**: 5个测试全部通过，覆盖率达标 ✅

---

### Task 2.3: VectorStore 向量存储
**类型**: feat
**文件**: `backend/app/memory/vector_store.py`, `backend/tests/test_vector_store.py`

- [ ] 2.3.1 RED: 编写 `test_store_message_embedding` - 存储消息向量
- [ ] 2.3.2 RED: 编写 `test_store_segment_embedding` - 存储段摘要向量
- [ ] 2.3.3 RED: 编写 `test_search_by_similarity` - 相似度搜索
- [ ] 2.3.4 RED: 编写 `test_search_with_threshold` - 阈值过滤
- [ ] 2.3.5 RED: 编写 `test_search_filter_by_session` - 会话过滤
- [ ] 2.3.6 RED: 编写 `test_generate_embedding` - 向量生成
- [ ] 2.3.7 GREEN: 实现 `VectorStore` 类
- [ ] 2.3.8 GREEN: 实现 `store_message_embedding()` 方法
- [ ] 2.3.9 GREEN: 实现 `store_segment_embedding()` 方法
- [ ] 2.3.10 GREEN: 实现 `search()` 方法
- [ ] 2.3.11 GREEN: 实现 `_generate_embedding()` 方法（使用 embedding 模型）
- [ ] 2.3.12 REFACTOR: 优化批量处理能力
- [ ] 2.3.13 VERIFY: 运行测试，覆盖率 ≥ 80%

**验收**: 6个测试全部通过，覆盖率达标 ✅

---

### Task 2.4: SmartMemoryManager 智能记忆管理器
**类型**: feat
**文件**: `backend/app/memory/manager.py`, `backend/tests/test_smart_memory_manager.py`

- [ ] 2.4.1 RED: 编写 `test_process_new_message_flow` - 消息处理流程
- [ ] 2.4.2 RED: 编写 `test_process_high_importance_message` - 高重要性处理
- [ ] 2.4.3 RED: 编写 `test_process_low_importance_message` - 低重要性处理
- [ ] 2.4.4 RED: 编写 `test_create_new_segment_on_topic_switch` - 主题切换创建段
- [ ] 2.4.5 RED: 编写 `test_update_existing_segment` - 更新现有段
- [ ] 2.4.6 RED: 编写 `test_get_context_with_summary` - 带摘要上下文
- [ ] 2.4.7 RED: 编写 `test_get_context_with_semantic_search` - 语义检索上下文
- [ ] 2.4.8 RED: 编写 `test_get_context_without_summary` - 无摘要上下文
- [ ] 2.4.9 RED: 编写 `test_error_handling_graceful_degradation` - 错误降级处理
- [ ] 2.4.10 GREEN: 重构现有 `MemoryManager` 为 `SmartMemoryManager`
- [ ] 2.4.11 GREEN: 实现 `process_new_message()` 方法
- [ ] 2.4.12 GREEN: 实现 `get_context()` 方法（替换现有逻辑）
- [ ] 2.4.13 GREEN: 实现 `_update_segment_summary()` 方法
- [ ] 2.4.14 GREEN: 集成 ImportanceScorer、TopicSegmenter、VectorStore
- [ ] 2.4.15 REFACTOR: 优化性能和错误处理
- [ ] 2.4.16 VERIFY: 运行测试，覆盖率 ≥ 80%

**验收**: 9个测试全部通过，覆盖率达标 ✅

---

**Phase 2 状态: ⬜ 待开始**

---

## Phase 3: API 集成与配置（TDD）

### Task 3.1: 更新 Pydantic 模型
**类型**: feat
**文件**: `backend/app/models.py`

- [ ] 3.1.1 RED: 编写模型验证测试
- [ ] 3.1.2 GREEN: 添加 `MessageImportance` 模型
- [ ] 3.1.3 GREEN: 添加 `MemorySegment` 模型
- [ ] 3.1.4 GREEN: 添加 `SearchResult` 模型
- [ ] 3.1.5 GREEN: 添加 `ProcessResult` 模型
- [ ] 3.1.6 GREEN: 更新 `Message` 模型，新增 importance_score 等字段
- [ ] 3.1.7 VERIFY: 运行测试确认通过

**验收**: 模型定义完整，测试通过 ✅

---

### Task 3.2: 更新聊天 API 集成智能记忆
**类型**: feat
**文件**: `backend/app/api/chat.py`

- [ ] 3.2.1 RED: 编写 `test_chat_with_smart_memory_integration` 测试
- [ ] 3.2.2 RED: 编写 `test_chat_importance_scored` 测试 - 验证重要性评分
- [ ] 3.2.3 RED: 编写 `test_chat_topic_segment_created` 测试 - 验证主题分段
- [ ] 3.2.4 GREEN: 更新 `chat()` 端点，注入 SmartMemoryManager
- [ ] 3.2.5 GREEN: 集成 `process_new_message()` 到消息处理流程
- [ ] 3.2.6 GREEN: 更新上下文获取逻辑，使用新的 `get_context()`
- [ ] 3.2.7 REFACTOR: 保持向后兼容（降级时回退到原逻辑）
- [ ] 3.2.8 VERIFY: 运行测试，覆盖率 ≥ 80%

**验收**: 聊天 API 集成完成，测试通过 ✅

---

### Task 3.3: 添加配置项
**类型**: chore
**文件**: `backend/app/config.py`

- [ ] 3.3.1 RED: 编写配置加载测试
- [ ] 3.3.2 GREEN: 添加 `SMART_MEMORY_CONFIG` 配置项
- [ ] 3.3.3 GREEN: 配置项包含：importance_model, embedding_model 等
- [ ] 3.3.4 GREEN: 添加环境变量支持
- [ ] 3.3.5 VERIFY: 运行测试确认通过

**验收**: 配置项可正常加载 ✅

---

**Phase 3 状态: ⬜ 待开始**

---

## Phase 4: 集成测试（TDD）

### Task 4.1: 核心流程集成测试（E2E）
**类型**: test
**文件**: `backend/tests/test_smart_memory_e2e.py`

- [ ] 4.1.1 编写测试：`test_smart_memory_e2e_flow`
- [ ] 4.1.2 实现 Step 1: 注册（test009 / 123456）
- [ ] 4.1.3 实现 Step 2: 登录获取 Token
- [ ] 4.1.4 实现 Step 3: 创建会话
- [ ] 4.1.5 实现 Step 4: 主题1聊天（Python学习，8轮）
- [ ] 4.1.6 实现 Step 5: 主题2聊天（数据库设计，6轮，第一次主题切换）
- [ ] 4.1.7 实现 Step 6: 主题3聊天（前端框架，6轮，第二次主题切换）
- [ ] 4.1.8 实现 Step 7.1: 验证重要性评分（重要消息 >= 0.6）
- [ ] 4.1.9 实现 Step 7.2: 验证主题分段（3个主题段）
- [ ] 4.1.10 实现 Step 7.3: 验证向量存储（>= 50% 重要消息）
- [ ] 4.1.11 实现 Step 7.4: 验证语义检索（正确召回历史）
- [ ] 4.1.12 实现 Step 8: 清理测试数据
- [ ] 4.1.13 配置 `pytest.mark.integration` 标记
- [ ] 4.1.14 添加环境变量检查：`ZHIPU_API_KEY`
- [ ] 4.1.15 运行测试确认通过（需要真实 API Key）

**验收**: E2E 测试通过，验证所有核心功能 ✅

---

**Phase 4 状态: ⬜ 待开始**

---

## Phase 5: 验证与文档

### Task 5.1: 运行完整测试套件
- [ ] 5.1.1 运行所有单元测试：`pytest backend/tests/test_importance*.py ...`
- [ ] 5.1.2 运行集成测试（需要 API Key）
- [ ] 5.1.3 检查覆盖率：`pytest --cov=app.memory --cov-report=term-missing`
- [ ] 5.1.4 确认覆盖率 ≥ 80%
- [ ] 5.1.5 确认无 Critical/High 级别代码问题

**验收**: 96+ 测试通过，覆盖率 ≥ 80% ✅

---

### Task 5.2: 更新文档
- [ ] 5.2.1 更新 `README.md` - 添加智能记忆特性说明
- [ ] 5.2.2 更新 `CLAUDE.md` - 添加 SmartMemoryManager 架构说明
- [ ] 5.2.3 添加智能记忆配置说明

**验收**: 文档已更新 ✅

---

**Phase 5 状态: ⬜ 待开始**

---

## 依赖关系

```
Phase 1: 数据库与 Repository
├── Task 1.1 (迁移)
├── Task 1.2 (Repository测试) ──▶ Task 1.3 (Repository实现)
└── Task 1.4 (扩展MessageRepo)
         │
         ▼
Phase 2: 核心组件
├── Task 2.1 (ImportanceScorer)
├── Task 2.2 (TopicSegmenter)
├── Task 2.3 (VectorStore)
└── Task 2.4 (SmartMemoryManager) ──▶ 依赖 2.1, 2.2, 2.3
         │
         ▼
Phase 3: API 集成
├── Task 3.1 (模型更新)
├── Task 3.2 (API集成) ──▶ 依赖 2.4
└── Task 3.3 (配置)
         │
         ▼
Phase 4: 集成测试
└── Task 4.1 (E2E测试) ──▶ 依赖 3.2
         │
         ▼
Phase 5: 验证与文档
└── Task 5.1, 5.2
```

---

## TDD 检查点（每个 Task 必须遵守）

### 开发前
- [ ] 已理解需求和验收标准
- [ ] 已编写测试用例（RED）
- [ ] 测试描述了预期行为
- [ ] 运行测试确认失败

### 开发后
- [ ] 已实现最小功能（GREEN）
- [ ] 运行测试确认通过
- [ ] 已重构优化（REFACTOR）
- [ ] 代码符合项目规范

### 提交前
- [ ] 测试覆盖率 ≥ 80%
- [ ] 无 Critical/High 级别问题
- [ ] 自我审查完成
- [ ] 用户（爸爸）确认

**禁止**：未经测试直接实现、覆盖率不达标、跳过检查点

---

## 当前状态

| Phase | 状态 | 说明 |
|-------|------|------|
| Phase 1: 数据库与 Repository | ⬜ 待开始 | 迁移脚本 + Repository |
| Phase 2: 核心组件 | ⬜ 待开始 | 4个核心组件 TDD |
| Phase 3: API 集成 | ⬜ 待开始 | 模型 + API + 配置 |
| Phase 4: 集成测试 | ⬜ 待开始 | E2E 流程测试 |
| Phase 5: 验证文档 | ⬜ 待开始 | 覆盖率 + 文档更新 |

---

**总测试数预计**: 32+ 单元测试 + 1 E2E 测试
**目标覆盖率**: ≥ 80%
**预计工时**: 16-20 小时（按 TDD 规范）
