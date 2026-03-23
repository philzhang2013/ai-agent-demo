# AI Agent Demo 项目配置

## 项目概述

这是一个 AI Agent 学习项目，用于系统性地学习和实践 AI Agent 开发。

### 学习路径

```
Demo 1: 命令行 Agent        →  理解 Agent 核心循环
Demo 2: Web 应用 Agent      →  学会流式输出 + 前端集成
Demo 3: 聊天机器人          →  掌握多轮对话 + 记忆管理
Demo 4: 自动化工具 Agent    →  实现工具调用 + 自主决策
```

### 技术栈

- **语言**：TypeScript / JavaScript
- **LLM 提供商**：ZhipuAI / MiniMax / Kimi
- **测试框架**：Vitest
- **包管理器**：npm

---

## 开发工作流 (MANDATORY)

⚠️ **严格遵守**：所有代码修改必须遵循以下工作流，**不得跳过任何步骤**。

### 完整工作流程

```
1. PLAN（规划）     → 理解需求，明确验收标准
2. TEST（测试）     → 先写测试，描述预期行为（RED）
3. CODE（编码）     → 编写最小实现使测试通过（GREEN）
4. VERIFY（验证）   → 运行所有测试，确保通过
5. REFACTOR（重构） → 优化代码，保持测试通过
6. REPORT（报告）   → 测试通过后才告知用户完成
```

---

## TDD 严格工作流 (MANDATORY)

### 规则 1: 测试优先原则

**MANDATORY** - 所有代码修改必须先写测试：

```bash
# 步骤 1: RED - 编写失败的测试
# 步骤 2: GREEN - 编写最小实现
# 步骤 3: REFACTOR - 重构优化
# 步骤 4: VERIFY - 验证所有测试
```

📖 **详细教程**：[TDD 工作流详解](./docs/tdd-workflow.md)

### 规则 2: 测试通过后才能报告

**MANDATORY** - 完成代码修改后必须：

1. **先运行单元测试**：`npm test`
2. **确认全部通过**：所有测试必须 ✅ PASS
3. **检查覆盖率**：`npm run test:coverage`，确保 ≥ 80%
4. **才告知用户完成**

**禁止行为**：
- ❌ 代码修改后不运行测试直接报告
- ❌ 测试失败时报告"完成"
- ❌ 只运行部分测试
- ❌ 跳过覆盖率检查

### 规则 3: 最小测试覆盖率：80%

所有代码必须达到 80% 以上的测试覆盖率。

```bash
npm run test:coverage
```

📖 **测试类型规范**：[测试类型和规范](./docs/testing-guide.md)

---

## 代码修改检查清单

每次修改代码前，必须确认：

- [ ] 已理解需求和验收标准
- [ ] 已编写/更新测试用例
- [ ] 测试描述了预期行为
- [ ] 运行测试确认 RED 状态（如果新测试）

每次修改代码后，必须确认：

- [ ] 所有测试通过 ✅
- [ ] 覆盖率 ≥ 80%
- [ ] 没有引入新的警告
- [ ] 没有破坏现有功能
- [ ] 代码符合项目规范

**只有以上全部确认后，才能告知用户"完成"。**

---

## 技术约定

📖 **详细规范**：[技术约定和代码规范](./docs/coding-standards.md)

### 核心原则

- **小文件优先** - 单文件 200-400 行，最多 800 行
- **高内聚低耦合** - 按功能/领域组织
- **类型安全** - TypeScript 严格模式
- **显式错误处理** - 每层都处理错误
- **不可变性** - 创建新对象，不修改原对象

---

## 目录结构

```
ai-agent-demo/
├── CLAUDE.md              # 项目配置（本文件）
├── README.md              # 项目说明
├── docs/                  # 📖 详细文档
│   ├── tdd-workflow.md    # TDD 工作流详解
│   ├── testing-guide.md   # 测试类型和规范
│   ├── coding-standards.md # 技术约定和代码规范
│   └── git-commands.md    # Git 常用命令
└── demos/
    ├── 01-cli-agent/      # 命令行 Agent
    ├── 02-web-agent/      # Web 应用 Agent
    ├── 03-chatbot/        # 聊天机器人
    └── 04-automation/     # 自动化工具 Agent
```

---

## 常用命令

```bash
# 开发
npm run dev              # 启动开发服务器
npm run dev:mock         # 模拟模式（不调用 API）

# 测试
npm test                 # 运行所有测试
npm run test:coverage    # 查看覆盖率
npm run test:ui          # UI 模式

# 构建
npm run build            # 编译 TypeScript
npm start                # 运行编译后的代码
```

---

## Git 提交规范 (MANDATORY)

⚠️ **重要**：所有提交必须遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范。

### 提交格式

```
<type>: <description>

<optional body>

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

### Type 类型

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 添加用户认证功能` |
| `fix` | 修复 Bug | `fix: 修复聊天消息未保存的问题` |
| `refactor` | 重构代码 | `refactor: 优化 Agent 类结构` |
| `docs` | 文档更新 | `docs: 更新 README 安装说明` |
| `test` | 测试相关 | `test: 添加用户登录测试` |
| `chore` | 构建/工具链 | `chore: 更新依赖版本` |

### Description 描述

- 使用中文
- 简洁明了，说明"做了什么"
- 首字母小写
- 不超过 50 个字符
- 结尾不加句号

### 推送到远端

⚠️ **MANDATORY**：推送代码到远端仓库前，**必须征得用户（爸爸）确认**。

📖 **Git 常用命令**：[Git 命令参考](./docs/git-commands.md)

---

## 延迟加载文档

以下文档按需加载，减少主配置文件大小：

| 文档 | 说明 | 何时阅读 |
|------|------|----------|
| [TDD 工作流详解](./docs/tdd-workflow.md) | RED-GREEN-REFACTOR 详细流程 | 学习 TDD 或遇到测试问题时 |
| [测试类型和规范](./docs/testing-guide.md) | 单元/集成/E2E 测试规范 | 编写测试时参考 |
| [技术约定和代码规范](./docs/coding-standards.md) | 代码组织和命名规范 | 编码时参考 |
| [Git 命令参考](./docs/git-commands.md) | Git 常用命令速查 | 需要 Git 操作时查询 |

---

## 参考资源

- [Vitest 文档](https://vitest.dev)
- [用户全局规则](~/.claude/rules/)
- [ZhipuAI API 文档](https://open.bigmodel.cn/dev/api)
- [测试驱动开发 (TDD)](https://en.wikipedia.org/wiki/Test-driven_development)
