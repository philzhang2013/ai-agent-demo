# 部署指南

## 后端部署

```bash
cd backend

# ⚠️ 确保虚拟环境已创建并激活
# 如果没有虚拟环境，先创建：
# python3 -m venv .venv

# 方式 1：使用虚拟环境 Python 直接运行（无需激活）
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# 方式 2：先激活虚拟环境，再运行
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**生产环境推荐参数**：

- `--host 0.0.0.0`：监听所有网络接口
- `--port 8000`：指定端口
- `--workers 4`：多 worker 进程（根据 CPU 核心数调整）
- 可配合进程管理器（如 systemd、supervisor）使用

## 前端部署

```bash
cd frontend

# 构建
npm run build

# 静态文件在 dist/ 目录
# 可以部署到任何静态文件服务器（Nginx、Apache、CDN 等）
```
