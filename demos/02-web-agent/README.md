# Demo 2 - Web Agent Demo

一个基于 Web 的 AI 智能助手应用，支持实时流式对话、用户认证、工具调用和会话管理。

## 📋 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [环境配置](#环境配置)
- [开发指南](#开发指南)
- [测试](#测试)
- [API 文档](#api-文档)
- [部署](#部署)

---

## ✨ 功能特性

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
- 会话列表查看
- 会话删除功能

---

## 🛠️ 技术栈

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

### 测试
- **pytest** - 后端单元测试
- **Playwright** - E2E 测试
- **Vitest** - 前端单元测试

---

## 📁 项目结构

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
│   │   ├── components/        # Vue 组件
│   │   ├── stores/            # Pinia 状态
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

---

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+
- Supabase 账号（用于数据库）

### 1. 克隆项目

```bash
cd demos/02-web-agent
```

### 2. 后端设置

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -e .

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要的配置

# 运行数据库迁移
psql $DATABASE_URL < migrations/001_initial_schema.sql

# 启动后端服务
uvicorn app.main:app --reload --port 8000
```

### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用

- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

---

## ⚙️ 环境配置

### 后端环境变量 (.env)

```bash
# 智谱 AI 配置
ZHIPUAI_API_KEY=your_api_key_here
ZHIPUAI_BASE_URL=https://open.bigmodel.cn/api/coding/paas/v4
ZHIPUAI_MODEL=glm-5

# 数据库配置
DATABASE_URL=postgresql://user:password@host:5432/dbname

# JWT 配置
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# 应用配置
APP_NAME=Web Agent Demo
APP_VERSION=0.1.0
LOG_LEVEL=INFO

# CORS 配置
FRONTEND_URL=http://localhost:5173
```

### Supabase 配置

1. 创建 Supabase 项目
2. 获取数据库连接字符串
3. 更新 `.env` 中的 `DATABASE_URL`
4. 运行数据库迁移脚本

---

## 📖 开发指南

### 后端开发

```bash
cd backend

# 运行测试
pytest

# 查看测试覆盖率
pytest --cov=app --cov-report=term-missing

# 生成 HTML 覆盖率报告
pytest --cov=app --cov-html
```

### 前端开发

```bash
cd frontend

# 运行单元测试
npm run test

# 运行 E2E 测试
npm run test:e2e

# E2E 测试调试模式
npm run test:e2e:debug

# 查看测试报告
npm run test:e2e:report

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

---

## 🧪 测试

### 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_auth.py

# 带覆盖率报告
pytest --cov=app --cov-report=html
```

### 前端 E2E 测试

```bash
cd frontend

# 运行所有 E2E 测试
npm run test:e2e

# 运行特定测试文件
npx playwright test e2e/auth.spec.ts

# 调试模式
npm run test:e2e:debug

# 可视化测试界面
npx playwright test --ui
```

**当前测试状态**：
- 后端单元测试：✅ 部分通过
- E2E 测试：⚠️ 4/21 通过

---

## 📚 API 文档

### RESTful API

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/api/health` | 健康检查 | ❌ |
| POST | `/api/auth/register` | 用户注册 | ❌ |
| POST | `/api/auth/login` | 用户登录 | ❌ |
| GET | `/api/auth/me` | 获取当前用户 | ✅ |
| POST | `/api/chat/stream` | 发送消息（SSE） | ❌ |
| GET | `/api/sessions` | 获取会话列表 | ✅ |
| GET | `/api/sessions/{id}` | 获取会话详情 | ✅ |
| DELETE | `/api/sessions/{id}` | 删除会话 | ✅ |

### SSE 事件流

```
event: token
data: {"content": "你"}

event: token
data: {"content": "好"}

event: tool_call
data: {"tool": "calculator", "args": {"expression": "18+25"}}

event: tool_result
data: {"content": "计算结果: 43"}

event: done
data: {"session_id": "uuid"}
```

详细 API 文档请访问：http://localhost:8000/docs

---

## 🚢 部署

### 后端部署

```bash
cd backend

# 确保虚拟环境已激活
source venv/bin/activate  # Windows: venv\Scripts\activate

# 确保依赖已安装
pip install -e .

# 生产环境运行
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**生产环境推荐参数**：
- `--host 0.0.0.0`：监听所有网络接口
- `--port 8000`：指定端口
- `--workers 4`：多 worker 进程（根据 CPU 核心数调整）
- 可配合进程管理器（如 systemd、supervisor）使用

### 前端部署

```bash
cd frontend

# 构建
npm run build

# 静态文件在 dist/ 目录
# 可以部署到任何静态文件服务器（Nginx、Apache、CDN 等）
```

---

## 📝 开发规范

### Git 提交规范

```
feat: 新功能
fix: 修复 bug
refactor: 重构代码
docs: 文档更新
test: 测试相关
chore: 构建/工具链相关
```

### 代码风格

- **Python**: 遵循 PEP 8
- **TypeScript/Vue**: 遵循 Vue 3 风格指南
- **测试**: TDD 开发模式（RED → GREEN → REFACTOR）

---

## 🔗 相关链接

- [Demo 1: 命令行 Agent](../01-cli-agent/README.md)
- [Demo 3: 聊天机器人](../03-chatbot/README.md)
- [智谱 AI 文档](https://open.bigmodel.cn/dev/api)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Vue 3 文档](https://vuejs.org/)

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📮 联系方式

如有问题，请提交 Issue 或联系项目维护者。

---

**最后更新**: 2026-03-22
