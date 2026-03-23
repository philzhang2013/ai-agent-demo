# Git 提交规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范。

---

## 提交格式

```
<type>: <description>

<optional body>

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

## Type 类型

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 添加用户认证功能` |
| `fix` | 修复 Bug | `fix: 修复聊天消息未保存的问题` |
| `refactor` | 重构代码 | `refactor: 优化 Agent 类结构` |
| `docs` | 文档更新 | `docs: 更新 README 安装说明` |
| `test` | 测试相关 | `test: 添加用户登录测试` |
| `chore` | 构建/工具链 | `chore: 更新依赖版本` |
| `perf` | 性能优化 | `perf: 优化数据库查询` |
| `ci` | CI 配置 | `ci: 添加 GitHub Actions` |

---

## Description 描述

- 使用中文
- 简洁明了，说明"做了什么"而非"怎么做的"
- 首字母小写
- 不超过 50 个字符
- 结尾不加句号

**✅ 好的示例**：
```
feat: 添加用户注册功能
fix: 修复 Token 过期问题
docs: 更新 API 文档
```

**❌ 不好的示例**：
```
Feat: Adding User Registration Function  # 首字母大写、英文
feat: 添加用户注册功能。                    # 结尾有句号
feat: 我修改了 UserController 的 register 方法来实现用户注册功能  # 太冗长
```

---

## Body 正文（可选）

详细描述修改内容，可以分点说明：

```
feat: 添加用户注册功能

- 添加用户名和密码验证
- 使用 bcrypt 加密密码
- 返回 JWT Token
- 添加单元测试，覆盖率 85%

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

## Co-Authored-By（可选）

当 Claude Code 参与代码编写时，添加：

```
Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

## 提交示例

```bash
# 新功能
git commit -m "feat: 添加流式聊天功能

- 实现 SSE 流式输出
- 支持多轮对话
- 添加断线重连

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"

# 修复 Bug
git commit -m "fix: 修复数据库连接泄漏问题"

# 文档更新
git commit -m "docs: 添加环境配置说明"

# 重构
git commit -m "refactor: 将 Agent 类拆分为多个模块"

# 测试
git commit -m "test: 添加用户认证集成测试"
```

---

## 推送到远端

⚠️ **MANDATORY**：推送代码到远端仓库前，**必须征得用户确认**。

```bash
# 1. 本地提交
git add .
git commit -m "feat: 添加新功能"

# 2. 询问用户
# "代码已提交到本地，是否推送到远端？"

# 3. 用户确认后再推送
git push
```

**禁止行为**：
- ❌ 未经用户确认直接 `git push`
- ❌ 跳过用户确认就推送代码

---

## 常用命令速查

```bash
# 查看状态
git status

# 查看历史
git log --oneline -10

# 查看差异
git diff

# 撤销修改
git restore <file>

# 撤销最后一次提交（保留修改）
git reset --soft HEAD~1

# 修改最后一次提交信息
git commit --amend
```
