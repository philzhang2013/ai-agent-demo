# Demo 2 - Web Agent Demo

一个基于 Web 的 AI 智能助手应用，支持实时流式对话、用户认证、工具调用和会话管理。

## 📚 文档导航

| 文档 | 说明 | 快速访问 |
|------|------|---------|
| [快速开始](docs/quick-start.md) | 安装步骤、环境配置 | [阅读 →](docs/quick-start.md) |
| [开发指南](docs/development.md) | 开发命令、环境变量、代码规范 | [阅读 →](docs/development.md) |
| [API 文档](docs/api-reference.md) | REST API、SSE 事件流、扩展指南 | [阅读 →](docs/api-reference.md) |
| [部署指南](docs/deployment.md) | 前后端部署说明 | [阅读 →](docs/deployment.md) |
| [系统架构](docs/architecture.md) | 功能特性、技术栈、项目结构、迭代进展 | [阅读 →](docs/architecture.md) |
| [更新日志](docs/changelog.md) | 版本更新记录 | [阅读 →](docs/changelog.md) |

## ✨ 功能特性

- 🔐 **用户认证** - JWT Token 认证、路由守卫
- 💬 **实时聊天** - SSE 流式输出、多轮对话
- 🛠️ **工具调用** - 计算器、天气查询，可扩展工具系统
- 📊 **会话管理** - 侧边栏列表、标题编辑、消息持久化
- 🧠 **智能记忆** - 长短记忆分层、主题分段、向量存储
  - 消息重要性自动评分
  - 对话按主题自动分段
  - 主题段语义向量存储
  - API 支持语义搜索历史记忆

## 🛠️ 技术栈

**后端**: Python 3.10+ · FastAPI · asyncpg · Pydantic · JWT
**前端**: Vue 3 · TypeScript · Vite · Element Plus · Pinia
**数据库**: PostgreSQL · pgvector
**测试**: pytest · Playwright · Vitest

## 🚀 快速开始

```bash
# 1. 后端设置（⚠️ 必须先创建虚拟环境）
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
# 编辑 .env 填入配置（DATABASE_URL 必须正确！）

# 2. 执行数据库迁移（⚠️ 必须使用 .env 中的 DATABASE_URL）
export $(cat .env | grep -v '^#' | xargs)
psql "$DATABASE_URL" -f migrations/001_initial_schema.sql

# 3. 启动后端服务
.venv/bin/uvicorn app.main:app --reload --port 8000

# 4. 前端设置（新终端）
cd frontend
npm install
npm run dev

# 5. 访问应用
# 前端: http://localhost:5173
# API:  http://localhost:8000
```

> ⚠️ **重要提醒**：所有数据库操作必须使用 `.env` 中的 `DATABASE_URL`，不要硬编码或使用默认连接。

详细说明请查看 [快速开始指南](docs/quick-start.md)。

## 📁 项目结构

```
02-web-agent/
├── backend/                 # Python FastAPI 后端
│   ├── app/
│   │   ├── agent/           # Agent 核心（对话、工具、流式）
│   │   ├── api/             # API 路由
│   │   ├── auth/            # JWT 认证
│   │   ├── memory/          # 📚 智能记忆系统
│   │   └── db/              # 数据库访问层
│   ├── tests/               # 后端测试
│   └── migrations/          # 数据库迁移
├── frontend/                # Vue 3 前端
│   ├── src/
│   │   ├── components/      # Vue 组件
│   │   ├── stores/          # Pinia 状态管理
│   │   └── api/             # API 客户端
│   └── e2e/                 # E2E 测试
└── docs/                    # 📚 项目文档
```

## 🗓️ 迭代进展

| 阶段 | 功能 | 状态 | 文档 |
|------|------|------|------|
| 基础 | 用户认证、实时聊天、工具调用、会话管理 | ✅ 已完成 | - |
| **A** | **长短记忆** - 固定阈值触发、摘要生成 | ✅ **已完成** | [design](openspec/changes/memory-tier-a-basic/design.md) |
| **B** | **智能记忆** - 重要性评分、主题分段、向量检索 | ✅ **已完成** | [design](openspec/changes/smart-memory/design.md) |
| C | 增强记忆 - 跨会话用户画像 | 📋 规划中 | - |

详细架构说明请查看 [系统架构文档](docs/architecture.md)。

## 🧪 测试

```bash
# 后端测试
cd backend
pytest
pytest --cov=app --cov-report=html

# 前端 E2E 测试
cd frontend
npm run test:e2e
```

## 🔗 相关链接

- [Demo 1: 命令行 Agent](../01-cli-agent/README.md)
- [智谱 AI 文档](https://open.bigmodel.cn/dev/api)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Vue 3 文档](https://vuejs.org/)

---

**最后更新**: 2026-03-27
