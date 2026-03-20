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
- **LLM 提供商**：ZhipuAI / OpenAI / Claude
- **测试框架**：Vitest
- **包管理器**：npm / pnpm / bun

---

## 开发工作流 (MANDATORY)

所有功能开发必须遵循以下工作流：

### 1. Plan First - 规划优先

- 使用 **Plan Mode** 进行实施规划
- 明确需求边界和验收标准
- 识别依赖关系和风险点
- 分解为可执行的步骤

### 2. TDD Approach - 测试驱动开发

**MANDATORY** - 所有代码必须先写测试：

```bash
# RED: 编写测试（预期行为）
# GREEN: 编写最小实现
# IMPROVE: 重构优化
# VERIFY: 验证覆盖率 80%+
```

测试类型要求：
- **单元测试** - 函数、类、组件
- **集成测试** - API 端点、数据库操作
- **E2E 测试** - 关键用户流程

### 3. Code Review - 代码审查

代码完成后，使用 **code-reviewer** agent 进行审查：
- 修复 CRITICAL 和 HIGH 问题
- 尽可能修复 MEDIUM 问题
- 确保符合编码规范

### 4. Commit - 提交代码

遵循 Conventional Commits 格式：
```
<type>: <description>

类型: feat, fix, refactor, docs, test, chore, perf, ci
```

---

## TDD 要求

### 最小测试覆盖率：80%

所有代码必须达到 80% 以上的测试覆盖率。

### 测试框架：Vitest

每个 Demo 应包含：
- `vitest.config.ts` - 测试配置
- `tests/` 目录 - 测试文件
- `package.json` - 测试脚本

### 测试脚本示例

```json
{
  "scripts": {
    "test": "vitest",
    "test:coverage": "vitest --coverage",
    "test:ui": "vitest --ui"
  }
}
```

### TDD 工作流示例

```bash
# 1. 编写测试（RED）
# 创建测试文件，描述预期行为

# 2. 运行测试（确认失败）
npm test

# 3. 编写实现（GREEN）
# 编写最小代码使测试通过

# 4. 运行测试（确认通过）
npm test

# 5. 重构（IMPROVE）
# 优化代码结构

# 6. 验证覆盖率
npm run test:coverage
```

---

## 技术约定

### 代码组织

- **小文件优先** - 单文件 200-400 行，最多 800 行
- **高内聚低耦合** - 按功能/领域组织
- **类型安全** - TypeScript 严格模式

### 错误处理

- **显式处理** - 每层都处理错误
- **友好提示** - UI 面向用户的友好消息
- **详细日志** - 服务端记录详细上下文
- **永不吞没** - 不静默忽略错误

### 不可变性 (CRITICAL)

- **创建新对象，不修改原对象**
- 防止隐藏副作用
- 便于调试和并发

### 模拟测试模式

为避免 API 调用消耗，支持模拟模式：

```typescript
// 环境变量控制
MOCK_LLM=true npm run dev

// 或在代码中判断
const isMock = process.env.MOCK_LLM === 'true';
```

---

## 目录结构

```
ai-agent-demo/
├── CLAUDE.md              # 项目配置（本文件）
├── README.md              # 项目说明
├── demos/
│   ├── 01-cli-agent/      # 命令行 Agent
│   │   ├── src/
│   │   │   ├── index.ts   # 主程序入口
│   │   │   ├── types.ts   # 类型定义
│   │   │   ├── tools.ts   # 工具函数
│   │   │   └── agent.ts   # Agent 类
│   │   ├── tests/         # 测试文件
│   │   ├── package.json
│   │   └── vitest.config.ts
│   ├── 02-web-agent/      # Web 应用 Agent
│   ├── 03-chatbot/        # 聊天机器人
│   └── 04-automation/     # 自动化工具 Agent
└── docs/                  # 学习笔记
```

---

## 参考资源

- [Vitest 文档](https://vitest.dev)
- [用户全局规则](~/.claude/rules/)
- [ZhipuAI API 文档](https://open.bigmodel.cn/dev/api)
