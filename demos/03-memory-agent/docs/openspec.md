### 工作流命令

| 命令 | 用途 | 使用场景 |
|------|------|----------|
| `/opsx:explore` | 探索模式 | 思考问题、调查代码库、理清需求 |
| `/opsx:propose` | 提议变更 | 快速创建新变更的完整提案 |
| `/opsx:apply` | 实施变更 | 按任务清单执行实现 |
| `/opsx:archive` | 归档变更 | 归档已完成的变更 |

#### 命令详细说明

**`/opsx:explore`** - 探索模式
- 用于思考、调查、理清需求
- 可以读取文件、搜索代码，但**不实现功能**
- 可视化、自由探索，无需固定流程

**`/opsx:propose`** - 提议新变更
- 一次性生成变更提案
- 创建：`proposal.md`、`design.md`、`tasks.md`
- 输入：变更名称（kebab-case）或功能描述

**`/opsx:apply`** - 实施变更
- 按任务清单逐项执行
- 自动读取相关上下文文件
- 显示实施进度

**`/opsx:archive`** - 归档变更
- 检查构件和任务完成状态
- 同步增量规范到主规范
- 移动变更到归档目录

### 常用 OpenSpec CLI 命令

```bash
# 列出所有变更
openspec list --json

# 查看变更状态
openspec status --change "<name>" --json

# 获取实施说明
openspec instructions apply --change "<name>" --json

# 新建变更
openspec new change "<name>"

# 同步规范
openspec sync specs --change "<name>"
```

### 工作流示例

```bash
# 1. 探索和理清需求
/opsx:explore

# 2. 创建变更提案
/opsx:propose add-user-profile

# 3. 实施变更
/opsx:apply add-user-profile

# 4. 完成后归档
/opsx:archive add-user-profile
```

---
### openspec工作流（强制）
/opsx:explore ──► /opsx:new ──► /opsx:continue ──► ... ──► /opsx:apply