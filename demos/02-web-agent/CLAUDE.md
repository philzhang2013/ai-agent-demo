# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Demo 2 - Web Agent 是一个全栈 AI 智能助手应用，展示流式输出、用户认证和工具调用。后端使用 Python FastAPI，前端使用 Vue 3 + TypeScript。

---

## 开发命令

### 后端 (Python/FastAPI)

```bash
cd backend

# 激活虚拟环境
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -e .  # 或 pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --port 8000

# 运行单元测试（带覆盖率，最低 80%）
pytest

# 运行单个测试文件
pytest tests/test_agent.py

# 查看覆盖率报告（HTML）
open htmlcov/index.html  # macOS
```

### 前端 (Vue/TypeScript)

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（代理后端 API 到 localhost:8000）
npm run dev

# 构建
npm run build

# 预览构建结果
npm run preview

# 运行单元测试
npm run test

# E2E 测试（需要后端和前端同时运行）
npm run test:e2e
npm run test:e2e:debug    # 调试模式
npm run test:e2e:report   # 查看报告
```

---

## 核心架构

### 后端架构

```
backend/app/
├── main.py          # FastAPI 应用入口，注册路由和 CORS
├── config.py        # Pydantic Settings 环境变量配置（单例模式）
├── models.py        # Pydantic 数据模型
│
├── agent/           # Agent 核心模块
│   ├── base.py      # Agent 类：处理对话、工具调用、流式输出
│   └── tools.py     # 工具定义：calculator, get_weather
│
├── providers/       # LLM 提供商抽象
│   ├── base.py      # LLMClient 基类接口
│   └── zhipuai.py   # 智谱 AI 实现（chat + chat_stream）
│
├── api/             # API 路由
│   ├── chat.py      # 聊天端点（POST /api/chat, /api/chat/stream）
│   ├── auth.py      # 认证端点（注册、登录）
│   ├── sessions.py  # 会话管理（列表、详情、删除）
│   └── health.py    # 健康检查
│
├── auth/            # 认证模块
│   ├── jwt.py       # JWT Token 生成/验证
│   ├── password.py  # bcrypt 密码哈希
│   ├── dependencies.py  # FastAPI 依赖注入（get_current_user）
│   └── repository.py # 用户数据访问
│
└── db/              # 数据库模块
    ├── connection.py    # asyncpg 连接池管理
    └── repositories.py  # Repository 模式数据访问层
```

**关键设计模式**：
- **Provider 抽象**：`LLMClient` 基类定义 `chat()` 和 `chat_stream()` 接口，便于扩展其他 LLM 提供商
- **Agent 循环**：`Agent.process_message()` 实现 ReAct 循环（调用 LLM → 执行工具 → 再次调用 LLM → ...）
- **SSE 流式**：`/api/chat/stream` 使用 `sse-starlette` 逐 token 返回
- **Repository 模式**：数据库操作封装在 repositories 中

### 前端架构

```
frontend/src/
├── main.ts          # 应用入口，初始化 Pinia + Router + Element Plus
├── App.vue          # 根组件
│
├── api/             # API 客户端
│   ├── chat.ts      # ChatAPI 类：SSE 流式处理（fetch + ReadableStream）
│   └── types.ts     # TypeScript 类型定义
│
├── stores/          # Pinia 状态管理
│   ├── auth.ts      # 用户认证状态
│   └── chat.ts      # 聊天消息状态
│
├── router/          # Vue Router 配置
│   └── index.ts     # 路由定义（/login, /chat）
│
├── components/      # Vue 组件
│   ├── AuthPage.vue       # 登录/注册页面
│   ├── ChatContainer.vue  # 聊天容器
│   ├── MessageList.vue    # 消息列表
│   └── InputBox.vue       # 输入框
│
└── views/           # 页面视图
```

**SSE 流式处理**：
- 前端使用 `fetch()` + `ReadableStream` 解析 SSE 格式
- 事件类型：`token`（文本）、`tool_call`（工具调用）、`tool_result`（结果）、`done`（结束）

---

## 环境配置

### 必需的环境变量 (backend/.env)

```bash
# LLM 提供商
ZHIPUAI_API_KEY=your_api_key_here
ZHIPUAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
ZHIPUAI_MODEL=glm-5

# 数据库（PostgreSQL）
DATABASE_URL=postgresql://user:password@host:5432/dbname

# JWT
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# 应用
FRONTEND_URL=http://localhost:5173
MAX_ITERATIONS=5
```

### 数据库迁移

```bash
cd backend
psql $DATABASE_URL < migrations/001_initial_schema.sql
# 或使用迁移脚本
python run_migration.py
```

---

## API 端点

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/api/health` | 健康检查 | ❌ |
| POST | `/api/auth/register` | 用户注册 | ❌ |
| POST | `/api/auth/login` | 用户登录（返回 JWT） | ❌ |
| GET | `/api/auth/me` | 获取当前用户 | ✅ |
| POST | `/api/chat` | 发送消息（非流式） | ❌ |
| POST | `/api/chat/stream` | 发送消息（SSE 流式） | ❌ |
| GET | `/api/sessions` | 获取会话列表 | ✅ |
| GET | `/api/sessions/{id}` | 获取会话详情 | ✅ |
| DELETE | `/api/sessions/{id}` | 删除会话 | ✅ |

API 文档：http://localhost:8000/docs

---

## 测试约定

- **后端测试**：`pytest`，最低覆盖率 80%，配置在 `pytest.ini`
- **前端 E2E**：`Playwright`，配置在 `playwright.config.ts`，仅测试 Chromium
- **TDD 工作流**：遵循 RED → GREEN → REFACTOR

---

## 扩展指南

### 添加新的 LLM 提供商

1. 在 `backend/app/providers/` 创建新文件（如 `openai.py`）
2. 继承 `LLMClient` 基类，实现 `chat()` 和 `chat_stream()`
3. 在 `agent/base.py` 的 `create_llm_client()` 中添加条件分支

### 添加新工具

1. 在 `backend/app/agent/tools.py` 定义工具函数
2. 创建 `Tool` 实例并添加到 `tools` 列表
3. 工具自动注册到 Agent 的 Function Calling 定义中
