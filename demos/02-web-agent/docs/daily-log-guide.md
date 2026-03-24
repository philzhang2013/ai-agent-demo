# 每日开发日志使用指南

> 记录每天的进度、遇到的问题和下一步计划
>
> **与 OpenSpec 工作流配合**：本日志记录高层进度，详细任务见各变更的 `tasks.md`

---

## 日志位置

`docs/daily-log.md`

---

## 日志结构

```markdown
## YYYY-MM-DD

### 🎯 当前变更
**变更简称** (变更目录名)
- 状态: Phase X 完成中
- 详细任务: `openspec/changes/{变更目录}/tasks.md`

### ✅ 今日完成
- ✅ `{变更简称}#P{阶段}.{任务}` - 任务描述
- ✅ `{变更简称}#P{阶段}.{任务}` - 任务描述

### 🐛 遇到的问题
| 问题描述 | 相关任务 | 解决方案 | 状态 |
|---------|---------|---------|------|
| 问题描述 | `{变更简称}#P{阶段}.{任务}` | 解决方案 | ✅ |

### 📅 明日计划
- [ ] `{变更简称}#P{阶段}.{任务}` - 计划任务

### 📝 备注
- 其他重要信息
```

---

## 任务引用格式

**格式**：`{变更简称}#P{阶段号}.{任务号}`

**示例**：
```markdown
# 完成整个 Phase
✅ `md-stream#P1` - Phase 1: Markdown 渲染

# 完成单个任务
✅ `md-stream#P1.1` - 添加依赖

# 计划中的任务
- [ ] `md-stream#P2.1` - 后端改造
```

---

## 状态标识

### 问题状态
- ✅ 已解决
- ⏳ 进行中
- ❌ 未解决
- 🚧 阻塞中

### 任务状态
- ✅ 已完成
- ⏳ 进行中
- 📅 计划中

---

## 常用变更简称

| 变更目录 | 简称 |
|---------|------|
| markdown-and-streaming-tools | md-stream |
| user-auth-enhancement | auth |
| chat-history-export | export |

---

## 与 OpenSpec 配合

```
OpenSpec 工作流                    每日日志
┌─────────────────┐              ┌─────────────────┐
│ /opsx:explore   │──记录到 ───▶│ docs/daily-log  │
│ /opsx:propose   │──进度 ──────▶│                 │
│ /opsx:apply     │──更新 ──────▶│                 │
│ /opsx:archive   │──完成 ──────▶│                 │
└─────────────────┘              └─────────────────┘
```

---

## 职责分工

| 文件 | 职责 | 粒度 |
|------|------|------|
| `openspec/changes/{变更}/tasks.md` | 详细任务清单 | 子任务、测试、验证 |
| `docs/daily-log.md` | 高层进度记录 | 每日完成、问题、计划 |

---

## 任务进度层级

```
项目级进度
    │
    ├─ docs/daily-log.md          每日工作日志
    │
    └─ openspec/changes/          OpenSpec 变更
            │
            └─ <change-name>/tasks.md   单变更任务清单
```

---

## 每日工作流程

```bash
# 1. 开始工作前
# 查看 daily-log.md 的昨日计划和问题
cat docs/daily-log.md

# 2. 执行开发
/opsx:apply some-feature

# 3. 结束工作前
# 更新 daily-log.md 今日进度

# 4. Git 提交
git add docs/daily-log.md
git commit -m "docs: 更新每日开发日志 YYYY-MM-DD"
```

---

## 实际示例

```markdown
## 2026-03-23

### 🎯 当前变更
**md-stream** (markdown-and-streaming-tools)
- 状态: Phase 1 已完成，Phase 2 待开始
- 详细任务: `openspec/changes/markdown-and-streaming-tools/tasks.md`

### ✅ 今日完成

#### Phase 1: Markdown 渲染 🎉
- ✅ `md-stream#P1.1` - 添加依赖
  - 添加 marked, dompurify, highlight.js
- ✅ `md-stream#P1.2` - 创建 MarkdownRenderer.vue 组件
  - 测试: 19 tests passed, 88.79% 覆盖率
- ✅ `md-stream#P1.3` - 集成到 MessageList.vue
  - 测试: 11 tests passed, 97.08% 覆盖率

**Phase 1 总计**: 30 tests passed ✅

### 🐛 遇到的问题

| 问题描述 | 相关任务 | 解决方案 | 状态 |
|---------|---------|---------|------|
| highlight.js vitest 报错 | `md-stream#P1.2` | 使用 jsdom 环境 | ✅ 已解决 |
| 代码块行号对齐 | `md-stream#P1.2` | CSS table 布局 | ✅ 已解决 |

### 📅 明日计划

#### md-stream Phase 2: 流式工具调用
- [ ] `md-stream#P2.1` - 后端流式处理改造
- [ ] `md-stream#P2.2` - Agent 流式工具执行

**预计时间**: 2-3 小时

### 📝 备注
- Phase 1 手动测试需启动前端验证
- 代码质量: 无 console.log, 无 TypeScript 错误
```
