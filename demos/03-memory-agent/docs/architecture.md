# 系统架构

## 功能特性

### 🔐 用户认证

- 用户注册和登录（用户名 + 密码）
- JWT Token 认证
- 路由守卫保护
- 自动登录状态保持

### 💬 实时聊天

- SSE (Server-Sent Events) 流式输出
- 多轮对话支持
- 消息历史记录
- 逐字显示效果

### 🛠️ 工具调用

- 计算器工具 - 数学计算
- 天气查询工具 - 模拟天气信息
- 可扩展的工具系统

### 📊 会话管理

- 会话历史持久化
- 用户数据隔离
- **会话列表侧边栏** - 实时显示所有会话
- **会话切换** - 快速切换不同会话
- **会话标题编辑** - 点击标题即可编辑
- 会话创建和删除功能
- 会话预览（最后一条消息、消息数量、更新时间）

### 🧠 智能记忆系统

**阶段A - 长短记忆**：
- **自动摘要生成** - 每5条消息自动生成会话摘要
- **智能上下文构建** - 摘要 + 最近消息混合发送给 LLM
- **并发安全** - PostgreSQL UPSERT 处理并发更新
- **失败容错** - 摘要生成失败不阻断主聊天流程
- **动态阈值** - 支持配置化的摘要触发间隔

**阶段B - 智能记忆**：
- **重要性评分** - 多因子智能评估消息重要性（技术关键词、句式、实体、动作词）
- **主题分段** - 自动检测主题切换，按主题组织消息
- **向量存储** - 1536维向量嵌入，支持语义相似度计算
- **语义搜索** - 基于向量相似度的历史消息检索
- **分层上下文** - 高重要性消息 + 主题段摘要构建智能上下文
- **配置化管理** - 可配置的相似度阈值、分段大小等参数

## 技术栈

### 后端

- **Python 3.10+** - 主要编程语言
- **FastAPI** - Web 框架
- **asyncpg** - 异步 PostgreSQL 驱动
- **Pydantic V2** - 数据验证
- **python-jose** - JWT 认证
- **bcrypt** - 密码加密
- **sse-starlette** - SSE 支持

### 前端

- **Vue 3** - 前端框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Element Plus** - UI 组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理

### 数据库

- **Supabase PostgreSQL** - 云数据库
- **pgvector** - PostgreSQL向量扩展（智能记忆系统使用）

### 测试

- **pytest** - 后端单元测试
- **Playwright** - E2E 测试
- **Vitest** - 前端单元测试

## 项目结构

```
02-web-agent/
├── backend/                    # Python 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── config.py          # 配置管理
│   │   ├── models.py          # Pydantic 数据模型
│   │   ├── agent/             # Agent 核心模块
│   │   │   ├── base.py        # Agent 基类
│   │   │   ├── streaming.py   # 流式输出
│   │   │   └── tools.py       # 工具定义
│   │   ├── providers/         # LLM 提供商
│   │   │   ├── base.py        # 基类接口
│   │   │   └── zhipuai.py     # 智谱 AI
│   │   ├── api/               # API 路由
│   │   │   ├── auth.py        # 认证端点
│   │   │   ├── chat.py        # 聊天端点
│   │   │   ├── sessions.py    # 会话管理
│   │   │   └── health.py      # 健康检查
│   │   ├── auth/              # 认证模块
│   │   │   ├── jwt.py         # JWT 工具
│   │   │   ├── password.py    # 密码哈希
│   │   │   └── dependencies.py # 依赖注入
│   │   ├── memory/              # 📚 智能记忆系统
│   │   │   ├── __init__.py
│   │   │   ├── config.py        # 智能记忆配置
│   │   │   ├── manager.py       # MemoryManager - 长短记忆管理
│   │   │   ├── smart_memory_manager.py  # SmartMemoryManager - 智能记忆管理
│   │   │   ├── importance_scorer.py     # ImportanceScorer - 重要性评分
│   │   │   ├── topic_segmenter.py       # TopicSegmenter - 主题分段
│   │   │   └── vector_store.py          # VectorStore - 向量存储
│   │   └── db/                # 数据库模块
│   │       ├── connection.py  # 连接管理
│   │       └── repositories.py # 数据访问层
│   ├── tests/                 # 后端测试
│   ├── migrations/            # 数据库迁移
│   ├── .env                   # 环境变量
│   ├── pyproject.toml         # Python 配置
│   └── pytest.ini             # pytest 配置
│
├── frontend/                   # Vue 前端
│   ├── src/
│   │   ├── main.ts            # 应用入口
│   │   ├── App.vue            # 根组件
│   │   ├── api/               # API 客户端
│   │   │   ├── chat.ts        # 聊天 API
│   │   │   ├── sessions.ts    # 会话 API
│   │   │   └── types.ts       # 类型定义
│   │   ├── components/        # Vue 组件
│   │   │   ├── SessionItem.vue     # 会话列表项
│   │   │   ├── SessionSidebar.vue  # 会话侧边栏
│   │   │   ├── ChatContainer.vue   # 聊天容器
│   │   │   ├── MessageList.vue     # 消息列表
│   │   │   └── InputBox.vue        # 输入框
│   │   ├── stores/            # Pinia 状态
│   │   │   ├── auth.ts        # 认证状态
│   │   │   ├── chat.ts        # 聊天状态
│   │   │   └── sessionStore.ts # 会话状态
│   │   └── router/            # 路由配置
│   ├── e2e/                   # E2E 测试
│   ├── public/                # 静态资源
│   ├── index.html
│   ├── vite.config.ts
│   ├── playwright.config.ts   # Playwright 配置
│   └── package.json
│
└── README.md                   # 本文件
```

## 迭代进展表

| 阶段 | 功能模块 | 主要特性 | 状态 | 文档 |
|------|---------|---------|------|------|
| **基础** | 用户认证 | JWT 登录/注册、路由守卫 | ✅ 已完成 | - |
| **基础** | 实时聊天 | SSE 流式输出、多轮对话 | ✅ 已完成 | - |
| **基础** | 工具调用 | 计算器、天气查询 | ✅ 已完成 | - |
| **基础** | 会话管理 | 会话 CRUD、列表 UI、标题编辑 | ✅ 已完成 | - |
| **基础** | 消息持久化 | 消息保存、历史记录 | ✅ 已完成 | - |
| **A** | **长短记忆** | **固定阈值触发、摘要生成、混合上下文** | ✅ **已完成** | [design](../openspec/changes/memory-tier-a-basic/design.md) |
| **B** | **智能记忆** | **重要性评分、主题分段、向量存储、语义搜索** | ✅ **已完成** | [design](../openspec/changes/smart-memory/design.md) |
| **C** | 增强记忆 | 跨会话用户画像、长期偏好学习 | 📋 规划中 | - |

### 阶段说明

```
┌─────────────────────────────────────────────────────────────────┐
│                      记忆系统演进路线图                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  阶段A              阶段B              阶段C                     │
│  ✅已完成            ✅已完成            📋规划中                 │
│  ─────────────      ─────────────      ─────────────            │
│                                                                  │
│  ┌───────────┐      ┌───────────┐      ┌───────────┐            │
│  │ 固定阈值   │      │ 智能评分   │      │ 多维度    │            │
│  │ >=10条    │  ──▶ │ 主题分段   │  ──▶ │ 语义触发   │            │
│  │ 基础摘要   │      │ 向量存储   │      │ 知识图谱   │            │
│  └───────────┘      └───────────┘      └───────────┘            │
│                                                                  │
│  ┌───────────┐      ┌───────────┐      ┌───────────┐            │
│  │ 单会话    │      │ 会话内     │      │ 跨会话    │            │
│  │ 摘要      │  ──▶ │ 主题记忆   │  ──▶ │ 用户画像   │            │
│  │           │      │           │      │ 长期偏好   │            │
│  └───────────┘      └───────────┘      └───────────┘            │
│                                                                  │
│  ┌───────────┐      ┌───────────┐      ┌───────────┐            │
│  │ 简单      │      │ 分层      │      │ 向量检索  │            │
│  │ Prompt    │  ──▶ │ 压缩      │  ──▶ │ + RAG     │            │
│  │ 拼接      │      │ 智能召回   │      │ 全局搜索   │            │
│  └───────────┘      └───────────┘      └───────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 当前阶段详情：阶段A - 长短记忆基础 ✅ 已完成

**目标**：解决长对话上下文过长问题，实现基础的记忆分层

**核心机制**：
- **长记忆**：会话历史摘要（`memory_summaries` 表），每5条消息生成/更新
- **短记忆**：最近3条原始消息（有摘要时）或最近5条（无摘要时）
- **触发条件**：消息数达到 5, 10, 15, 20... 时触发摘要生成
- **上下文构建**：摘要 + 最近消息混合发送给 LLM

**技术实现**：
- `MemoryManager`：核心管理类（`app/memory/manager.py`）
  - `should_summarize(session_id)` - 判断是否触发摘要
  - `generate_summary(messages)` - 生成会话摘要
  - `get_context(session_id)` - 构建 LLM 上下文
- `MemorySummaryRepository`：摘要数据访问（`app/db/repositories.py`）
- PostgreSQL UPSERT：使用 `ON CONFLICT DO UPDATE` 处理并发
- 严格 TDD：96个测试通过，核心业务逻辑 100% 覆盖

**数据库迁移**：
```bash
# 运行记忆系统数据库迁移
psql $DATABASE_URL < migrations/003_add_memory_summaries.sql
```

**架构文档**：
- [提案文档](../openspec/changes/memory-tier-a-basic/proposal.md)
- [设计文档](../openspec/changes/memory-tier-a-basic/design.md)
- [任务分解](../openspec/changes/memory-tier-a-basic/tasks.md)
- [架构评审](../openspec/changes/memory-tier-a-basic/architecture-review.md)

### 当前阶段详情：阶段B - 智能记忆 ✅ 已完成

**目标**：实现智能记忆分层，支持重要性评估、主题分段和语义检索

**核心机制**：
- **重要性评分**：基于规则的多因子评分算法（技术关键词、句式、实体、动作词）
- **主题分段**：Jaccard相似度 + 主题词重叠检测，多策略边界判定
- **向量存储**：1536维向量嵌入，支持语义相似度检索
- **分层上下文**：高重要性消息 + 主题段摘要构建上下文

**技术实现**：
- `ImportanceScorer`：重要性评估（`app/memory/importance_scorer.py`）
  - `score()` - 单条消息评分
  - `score_batch()` - 批量评分
- `TopicSegmenter`：主题分段（`app/memory/topic_segmenter.py`）
  - `segment()` - 消息列表分段
  - `_calculate_similarity()` - 相似度计算
- `VectorStore`：向量管理（`app/memory/vector_store.py`）
  - `embed()` - 生成向量嵌入
  - `cosine_similarity()` - 余弦相似度计算
- `SmartMemoryManager`：智能记忆管理（`app/memory/smart_memory_manager.py`）
  - `process_message()` - 处理消息并评分
  - `create_topic_segments()` - 创建主题段
  - `semantic_search()` - 语义搜索
  - `build_context()` - 构建智能上下文

**数据库迁移**：
```bash
# 运行智能记忆系统数据库迁移
psql $DATABASE_URL < migrations/004_add_smart_memory.sql
```

**新增API端点**：
| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| POST | `/api/chat/{session_id}/analyze` | 分析会话记忆，生成主题段 | 可选 |
| GET | `/api/chat/{session_id}/memory` | 获取/语义搜索会话记忆 | 可选 |

**测试覆盖**：
- 66个测试全部通过
- ImportanceScorer: 90% 覆盖率
- TopicSegmenter: 92% 覆盖率
- SmartMemoryManager: 85% 覆盖率
- VectorStore: 76% 覆盖率

**架构文档**：
- [提案文档](../openspec/changes/smart-memory/proposal.md)
- [设计文档](../openspec/changes/smart-memory/design.md)
- [规格说明](../openspec/changes/smart-memory/specs/)
- [任务分解](../openspec/changes/smart-memory/tasks.md)
