# 开发指南

## 环境配置

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

```bash
cd backend
export $(cat .env | grep -v '^#' | xargs)
psql "$DATABASE_URL" -f migrations/001_initial_schema.sql
```

## 数据库操作规范

**Claude Code 执行所有数据库操作时必须使用 .env 中的 DATABASE_URL**

```bash
# 正确方式：从 .env 加载环境变量
cd backend
export $(cat .env | grep -v '^#' | xargs)

# 检查表结构
psql "$DATABASE_URL" -c "\dt"

# 查看 embedding 维度
psql "$DATABASE_URL" -c "SELECT atttypmod FROM pg_attribute WHERE attrelid = 'messages'::regclass AND attname = 'embedding';"

# 执行迁移
psql "$DATABASE_URL" -f migrations/xxx.sql
```

> ⚠️ **禁止**：直接使用 `psql` 或硬编码连接信息，这可能导致操作错误的数据库！

## 后端开发

```bash
cd backend

# 运行测试
pytest

# 查看测试覆盖率
pytest --cov=app --cov-report=term-missing

# 生成 HTML 覆盖率报告
pytest --cov=app --cov-html
```

## 前端开发

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

## 开发规范

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
