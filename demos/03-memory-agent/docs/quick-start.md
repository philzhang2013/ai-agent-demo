# 快速开始

## 前置要求

- Python 3.10+
- Node.js 18+
- PostgreSQL 数据库（本地或 Supabase）

## 1. 克隆项目

```bash
cd demos/03-memory-agent
```

## 2. 后端设置

**⚠️ 重要：必须先创建 Python 虚拟环境**

```bash
cd backend

# 步骤 1：创建虚拟环境（.venv）
python3 -m venv .venv

# 步骤 2：激活虚拟环境
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# 步骤 3：安装依赖
pip install -e .

# 步骤 4：配置环境变量（重要！）
cp .env.example .env
# 编辑 .env 文件，填入必要的配置（特别是 DATABASE_URL）

# 步骤 5：运行数据库迁移（⚠️ 必须使用 .env 中的 DATABASE_URL）
# 先加载环境变量
export $(cat .env | grep -v '^#' | xargs)
# 然后执行迁移
psql "$DATABASE_URL" -f migrations/001_initial_schema.sql
psql "$DATABASE_URL" -f migrations/002_add_session_title.sql
psql "$DATABASE_URL" -f migrations/003_add_memory_summaries.sql
psql "$DATABASE_URL" -f migrations/004_add_smart_memory.sql  # 智能记忆系统

# 步骤 6：启动后端服务
# 方式 A：使用虚拟环境 Python 直接启动（推荐，不需要激活虚拟环境）
.venv/bin/uvicorn app.main:app --reload --port 8000

# 方式 B：如果已激活虚拟环境，直接使用
# uvicorn app.main:app --reload --port 8000

# 关闭服务
pkill -f uvicorn
```

**常见错误**：
- `ModuleNotFoundError`: 虚拟环境未激活或未安装依赖
- 确保每次启动服务前虚拟环境已激活，或使用 `.venv/bin/uvicorn` 直接调用

## 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 4. 访问应用

- 前端：[http://localhost:5173](http://localhost:5173)
- 后端 API：[http://localhost:8000](http://localhost:8000)
- API 文档：[http://localhost:8000/docs](http://localhost:8000/docs)
