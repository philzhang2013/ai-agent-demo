# CLAUDE.md

> 本文件提供 Claude Code 工作时的核心架构指导
>
> 详细工作流和规范请参考 [docs/](./docs/) 目录

---

## 项目概述

Demo 2 - Web Agent 是一个全栈 AI 智能助手应用，展示流式输出、用户认证和工具调用。

**技术栈**：Python FastAPI · Vue 3 + TypeScript · ZhipuAI

**详细文档**：[README.md](./README.md)

---

## 目录结构

```
02-web-agent/
├── .claude/          # Claude Code 配置
├── backend/          # Python FastAPI 后端
├── frontend/         # Vue 3 前端
├── docs/             # 📚 项目文档（工作流、规范）
├── openspec/         # OpenSpec 工作流系统
├── CLAUDE.md         # 本文件 - 核心架构
└── README.md         # 项目说明
```

---

## 核心架构

### 后端 (FastAPI)

```
backend/app/
├── main.py          # 应用入口
├── config.py        # 环境变量配置（Pydantic Settings）
├── models.py        # 数据模型
├── agent/           # Agent 核心（对话、工具、流式）
├── providers/       # LLM 抽象（base + zhipuai）
├── api/             # 路由（chat, auth, sessions, health）
├── auth/            # 认证（JWT, password, dependencies）
├── db/              # 数据库（connection, repositories）
└── memory/          # 📚 长短记忆系统（阶段A）
    └── manager.py   # MemoryManager - 摘要生成、上下文构建
```

**关键模式**：

- **Provider 抽象** - `LLMClient` 接口便于扩展
- **Agent 循环** - ReAct 模式（LLM → 工具 → LLM）
- **SSE 流式** - 逐 token 返回
- **Repository** - 数据访问封装
- **MemoryManager** - 分层记忆管理（长记忆摘要 + 短记忆消息）

### 前端 (Vue 3)

```
frontend/src/
├── main.ts          # 入口
├── api/             # API 客户端（chat.ts + types.ts）
├── stores/          # Pinia 状态（auth, chat）
├── router/          # Vue Router
├── components/      # 组件
└── views/           # 页面
```

**SSE 处理**：`fetch()` + `ReadableStream` 解析事件

---

## 工作流和规范


| 文档                                         | 说明      | 何时阅读     |
| ------------------------------------------ | ------- | -------- |
| [OpenSpec 规范](./docs/openspec.md)          | 变更管理工作流 | 创建/实施变更时 |
| [Git Worktree 工作流](./docs/git-workflow.md) | 并行开发流程  | 功能开发时    |
| [每日日志指南](./docs/daily-log-guide.md)        | 进度追踪规范  | 记录进度时    |
| [测试规范](./docs/testing.md)                  | TDD 工作流 | 编写测试时    |


### OpenSpec 快速参考

```bash
# 探索需求
/opsx:explore

# 创建提案
/opsx:propose <change-name>

# 实施变更
/opsx:apply <change-name>

# 归档完成
/opsx:archive <change-name>
```

### Git Worktree 快速参考

```bash
# 创建 worktree
git worktree add .claude/worktrees/{name} -b feature/{name}

# 列出 worktree
git worktree list

# 删除 worktree
git worktree remove .claude/worktrees/{name}
```

---

## 开发命令

### 后端

```bash
cd backend

# ⚠️ 确保虚拟环境已创建（只需执行一次）
python3 -m venv .venv

# 方式 1：使用虚拟环境 Python 直接运行（推荐）
.venv/bin/uvicorn app.main:app --reload --port 8000

# 方式 2：先激活虚拟环境，再运行
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# 测试（虚拟环境激活后）
pytest

# 覆盖率（虚拟环境激活后）
pytest --cov=app --cov-report=html
```

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 运行
npm run dev

# 测试
npm test

# 覆盖率
npm run test:coverage

# 构建
npm run build
```

---

# ✅ 强制规范（MANDATORY）

## 1. 项目配置信息位于

Claude Code 当前项目的配置信息都在 [env](./backend/.env)中，包含的配置
- 数据库连接信息
- 智普Key
- Kimi Key
- 默认LLM供应商
- ...等等


# 📌 PostgreSQL 表结构变更规范（强制）

## 1. 基本原则

- **所有数据库表结构变更必须通过 `psql` 执行**
- **使用 (./backend/.env) 中的 DATABASE_URL，禁止硬编码连接信息**
- **禁止通过以下方式修改表结构：**
  - ❌ Python 脚本自动建表/改表
  - ❌ ORM 自动 migration（如 SQLAlchemy auto-migrate）
  - ❌ 手动在 GUI 工具（Navicat / DBeaver）中修改
- ## 所有变更必须是：
  - ✅ 显式 SQL
  - ✅ 可审查（Reviewable）
  - ✅ 可回滚（Rollbackable）

---

## 4.Migration 文件规范

## 3. Migration 文件规范（强化版，Claude Code 强制理解）

### ✅ 核心规则（必须遵守）

- **所有表结构变更必须以 `.sql` 文件形式存在**
- **每一次变更 = 一个独立 SQL 文件**
- **禁止在代码中内嵌或动态生成建表/改表 SQL**

---

### 📌 命名规范（强约束）

```text
<日期>_<feature_name>.sql
```

### migrations目录

```
/backend/migrations
  ├── 20260326_init_tables.sql
  ├── 20260326_add_messages_table.sql
  ├── 20260326_add_embedding_column.sql
```

## 3. 代码约定

- **测试覆盖率**：≥ 80%
- **提交规范**：[Conventional Commits](../../docs/git-commit-convention.md)
- **代码审查**：修改前自我审查，修改后请求审查
- **不可变性**：创建新对象，不修改原对象
- **错误处理**：显式处理，不吞没异常

---

## 4. 文档索引

```
docs/
├── openspec.md           # OpenSpec 工作流详细说明
├── git-workflow.md       # Git Worktree 并行开发
├── daily-log-guide.md    # 每日日志使用指南
├── testing.md            # 测试规范和 TDD 工作流
├── daily-log.md          # 每日开发日志实例
├── 项目指导.md           # 项目指导文档
└── 复盘0322.md           # 开发复盘记录
```

