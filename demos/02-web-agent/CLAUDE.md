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
└── db/              # 数据库（connection, repositories）
```

**关键模式**：
- **Provider 抽象** - `LLMClient` 接口便于扩展
- **Agent 循环** - ReAct 模式（LLM → 工具 → LLM）
- **SSE 流式** - 逐 token 返回
- **Repository** - 数据访问封装

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

| 文档 | 说明 | 何时阅读 |
|------|------|----------|
| [OpenSpec 规范](./docs/openspec.md) | 变更管理工作流 | 创建/实施变更时 |
| [Git Worktree 工作流](./docs/git-workflow.md) | 并行开发流程 | 功能开发时 |
| [每日日志指南](./docs/daily-log-guide.md) | 进度追踪规范 | 记录进度时 |
| [测试规范](./docs/testing.md) | TDD 工作流 | 编写测试时 |

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

# 运行
uvicorn app.main:app --reload

# 测试
pytest

# 覆盖率
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

## 代码约定

- **测试覆盖率**：≥ 80%
- **提交规范**：[Conventional Commits](../../docs/git-commit-convention.md)
- **代码审查**：修改前自我审查，修改后请求审查
- **不可变性**：创建新对象，不修改原对象
- **错误处理**：显式处理，不吞没异常

---

## 文档索引

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
