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
# 描述预期行为，此时测试应该失败

# 步骤 2: GREEN - 编写最小实现
# 只写刚好能让测试通过的代码

# 步骤 3: REFACTOR - 重构优化
# 在保持测试通过的前提下优化代码

# 步骤 4: VERIFY - 验证所有测试
# 运行完整测试套件，确保没有破坏现有功能
```

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
# 检查覆盖率
npm run test:coverage

# 输出示例（必须 ≥ 80%）：
# Files  2 passed (2)
# Tests  42 passed (42)
# Coverage  85.3%  (目标: ≥ 80%)
```

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

## TDD 工作流详解

### 1. RED 阶段 - 编写测试

```typescript
// tests/calculator.test.ts

import { describe, it, expect } from 'vitest';
import { calculatorTool } from '../src/tools.js';

describe('calculatorTool', () => {
  it('应该正确执行加法运算', async () => {
    // Arrange: 准备测试数据
    const input = { expression: '18 + 25' };

    // Act: 执行被测试的功能
    const result = await calculatorTool.execute(input);

    // Assert: 验证结果
    expect(result).toBe('计算结果: 18 + 25 = 43');
  });
});
```

**运行测试，确认失败（RED）：**
```bash
npm test

# 预期输出：
# ❌ tests/calculator.test.ts > calculatorTool > 应该正确执行加法运算
# Error: calculatorTool is not defined...
```

### 2. GREEN 阶段 - 编写实现

```typescript
// src/tools.ts

export const calculatorTool: Tool = {
  name: 'calculator',
  description: '执行数学计算',

  execute: (args) => {
    const expression = args.expression.trim();
    const result = Function('"use strict"; return (' + expression + ')')();
    return `计算结果: ${expression} = ${result}`;
  }
};
```

**运行测试，确认通过（GREEN）：**
```bash
npm test

# 预期输出：
# ✅ tests/calculator.test.ts > calculatorTool > 应该正确执行加法运算
```

### 3. REFACTOR 阶段 - 优化代码

在保持测试通过的前提下优化代码：

```typescript
// 添加错误处理
export const calculatorTool: Tool = {
  // ...
  execute: (args) => {
    try {
      const expression = args.expression.trim();
      const result = Function('"use strict"; return (' + expression + ')')();
      return `计算结果: ${expression} = ${result}`;
    } catch (error) {
      return `计算错误: ${error}`;
    }
  }
};
```

**运行测试，确保仍然通过：**
```bash
npm test

# 预期输出：所有测试 ✅
```

### 4. VERIFY 阶段 - 完整验证

```bash
# 1. 运行所有测试
npm test

# 2. 检查覆盖率
npm run test:coverage

# 3. 确认结果
# ✅ Tests  42 passed (42)
# ✅ Coverage  85.3%
```

---

## 测试类型要求

### 单元测试 (Unit Tests)

**MANDATORY** - 每个函数/类都需要单元测试：

```typescript
describe('工具函数', () => {
  describe('calculator', () => {
    it('应该执行加法', async () => { /* ... */ });
    it('应该执行减法', async () => { /* ... */ });
    it('应该处理错误输入', async () => { /* ... */ });
  });
});
```

### 集成测试 (Integration Tests)

测试多个组件协作：

```typescript
describe('Agent 集成测试', () => {
  it('应该完成完整的工具调用流程', async () => {
    const agent = new Agent({ mockMode: true });
    const response = await agent.processUserInput('计算 18 + 25');
    expect(response).toContain('43');
  });
});
```

### E2E 测试 (End-to-End Tests)

测试关键用户流程：

```typescript
describe('用户流程', () => {
  it('应该处理天气查询', async () => { /* ... */ });
  it('应该处理连续对话', async () => { /* ... */ });
});
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
│   │   │   ├── agent.ts   # Agent 类
│   │   │   └── logger.ts  # 日志工具
│   │   ├── tests/         # 测试文件
│   │   ├── package.json
│   │   └── vitest.config.ts
│   ├── 02-web-agent/      # Web 应用 Agent
│   ├── 03-chatbot/        # 聊天机器人
│   └── 04-automation/     # 自动化工具 Agent
└── docs/                  # 学习笔记
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

## 参考资源

- [Vitest 文档](https://vitest.dev)
- [用户全局规则](~/.claude/rules/)
- [ZhipuAI API 文档](https://open.bigmodel.cn/dev/api)
- [测试驱动开发 (TDD)](https://en.wikipedia.org/wiki/Test-driven_development)
