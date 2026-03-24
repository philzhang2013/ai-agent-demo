# Git Worktree 并行开发工作流

> 本项目使用 Git Worktree 实现功能并行开发，避免频繁切换分支

---

## 目录结构

```
02-web-agent/                      # 主仓库 (main)
├── .claude/worktrees/             # worktree 存放目录
│   ├── md-stream/                 # 功能 worktree
│   ├── user-auth/                 # 并行功能 worktree
│   └── bugfix-hotfix/             # 紧急修复 worktree
├── openspec/changes/              # 变更提案（共享）
└── ...
```

---

## 完整工作流

### 阶段 1：探索（主仓库）

```bash
# 在主仓库进行探索
/opsx:explore

# 探索完成后，决定是否创建变更
```

### 阶段 2：提案（主仓库）

```bash
# 在主仓库创建变更提案
/opsx:propose add-user-profile

# 提案创建后，询问是否创建 worktree
```

### 阶段 3：创建 Worktree

```bash
# 格式：git worktree add .claude/worktrees/{简称} -b {分支名}
git worktree add .claude/worktrees/md-stream -b feature/markdown-streaming

# 切换到 worktree 工作目录
cd .claude/worktrees/md-stream

# 验证分支
git branch  # 应显示 * feature/markdown-streaming
```

### 阶段 4：实施（在 Worktree 中）

```bash
cd .claude/worktrees/md-stream

# 开始实施
/opsx:apply markdown-and-streaming-tools

# 遵循 TDD 工作流
# RED → GREEN → REFACTOR → VERIFY
```

### 阶段 5：并行开发示例

```
主仓库 (main)          - 探索新需求
worktree/md-stream/    - 功能开发中
worktree/user-auth/    - 功能开发中
```

```bash
# Terminal 1: 主仓库探索
/opsx:explore  # 探索 "聊天历史导出"

# Terminal 2: md-stream 开发
cd .claude/worktrees/md-stream
/opsx:apply markdown-and-streaming-tools

# Terminal 3: user-auth 开发
cd .claude/worktrees/user-auth
/opsx:apply user-auth-enhancement
```

### 阶段 6：完成并清理

```bash
cd .claude/worktrees/md-stream

# 1. 运行测试
npm test && pytest

# 2. 归档 OpenSpec 变更
/opsx:archive markdown-and-streaming-tools

# 3. 提交代码
git add .
git commit -m "feat: markdown 渲染和流式工具调用

- 添加 MarkdownRenderer 组件
- 实现代码高亮和行号
- 集成到 MessageList

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"

# 4. 推送到远程
git push -u origin feature/markdown-streaming

# 5. 创建 PR（可选）
gh pr create --title "feat: markdown 渲染和流式工具调用" --body "$(cat <<'EOF'
## 功能说明
- Markdown 渲染组件
- 代码高亮和行号
- XSS 防护

## 测试
- 单元测试: 30 tests passed
- 覆盖率: 88.79% (MarkdownRenderer), 97.08% (MessageList)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"

# 6. 合并后清理 worktree（回到主仓库执行）
cd ../..
git worktree remove .claude/worktrees/md-stream
git branch -d feature/markdown-streaming
```

---

## Worktree 管理命令

```bash
# 列出所有 worktree
git worktree list

# 删除 worktree（清理）
git worktree remove .claude/worktrees/md-stream

# 移动 worktree
git worktree move .claude/worktrees/md-stream .claude/worktrees/new-name

# 查看工作树状态
git worktree list --porcelain

# 清理 stale worktree
git worktree prune
```

---

## Worktree 与 OpenSpec 配合

```
OpenSpec 工作流                    Git Worktree
┌─────────────────┐              ┌─────────────────┐
│ /opsx:explore   │──在主仓库 ──▶│ main 分支       │
│ /opsx:propose   │──在主仓库 ──▶│ main 分支       │
│ /opsx:apply     │──创建并 ────▶│ worktree/{功能} │
│ /opsx:archive   │──在 worktree│ worktree/{功能} │
└─────────────────┘              └─────────────────┘
```

---

## 命名规范

| 类型 | Worktree 路径 | 分支名 |
|------|--------------|--------|
| 功能开发 | `.claude/worktrees/{变更简称}` | `feature/{描述}` |
| Bug 修复 | `.claude/worktrees/fix-{问题}` | `fix/{描述}` |
| 紧急修复 | `.claude/worktrees/hotfix-{问题}` | `hotfix/{描述}` |
| 重构 | `.claude/worktrees/refactor-{模块}` | `refactor/{描述}` |

**示例**：
- `md-stream` → `feature/markdown-streaming`
- `fix-login` → `fix/user-auth-login-error`
- `hotfix-api` → `hotfix/api-crash-fix`

---

## 每日工作流程

```bash
# 1. 开始工作前
# 查看当前 worktree
git worktree list

# 2. 切换到对应 worktree
cd .claude/worktrees/{功能名称}

# 3. 查看 daily-log.md 的昨日计划和问题

# 4. 执行开发
/opsx:apply some-feature

# 5. 结束工作前
# 更新 daily-log.md 今日进度

# 6. Git 提交
git add .
git commit -m "feat: 完成阶段 x"

# 7. 推送进度（可选）
git push
```

---

## 注意事项

⚠️ **重要**：
- `openspec/changes/` 目录在所有 worktree 中共享（Git 自动处理）
- 每个 worktree 有独立的 `.git` 文件指向主仓库
- 在 worktree 中提交不会影响主仓库的 staging area
- 删除 worktree 前确保工作已合并或推送

✅ **最佳实践**：
- 主仓库保持干净（main 分支）
- 每个功能使用独立 worktree
- 定期同步主仓库最新代码到 worktree
- 完成后及时清理 worktree
- 使用有意义的简称命名 worktree

---

## 常见问题

**Q: worktree 中如何更新主仓库的最新代码？**
```bash
cd .claude/worktrees/md-stream
git fetch origin main
git merge origin/main
```

**Q: 如何在 worktree 之间切换？**
```bash
# 不需要 git switch，直接 cd 到对应目录
cd .claude/worktrees/other-feature
```

**Q: worktree 删除后分支还在吗？**
```bash
# worktree 删除后分支仍然存在，需要单独删除
git branch -d feature/markdown-streaming
```
