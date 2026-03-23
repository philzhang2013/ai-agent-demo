# TDD 工作流详解

本文档详细说明测试驱动开发（TDD）的完整工作流程。

---

## 1. RED 阶段 - 编写测试

首先编写一个会失败的测试，描述我们期望的行为。

### 编写测试代码

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

### 运行测试，确认失败

```bash
npm test

# 预期输出（测试应该失败）：
# ❌ tests/calculator.test.ts > calculatorTool > 应该正确执行加法运算
# Error: calculatorTool is not defined...
```

**为什么要确认失败？**
- 验证测试确实在测试我们要实现的功能
- 确保测试不会意外通过（误报）
- 建立测试的"有效性"

---

## 2. GREEN 阶段 - 编写实现

编写刚好能让测试通过的最小代码。

### 编写实现代码

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

### 运行测试，确认通过

```bash
npm test

# 预期输出：
# ✅ tests/calculator.test.ts > calculatorTool > 应该正确执行加法运算
```

**为什么要最小实现？**
- 避免过度设计
- 快速验证思路
- 保持代码简洁
- 为重构留出空间

---

## 3. REFACTOR 阶段 - 优化代码

在保持测试通过的前提下，改进代码质量。

### 添加错误处理

```typescript
export const calculatorTool: Tool = {
  name: 'calculator',
  description: '执行数学计算',

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

### 添加边界情况测试

```typescript
describe('calculatorTool', () => {
  it('应该处理除零错误', async () => {
    const result = await calculatorTool.execute({ expression: '1 / 0' });
    expect(result).toContain('Infinity'); // 或者期望的错误消息
  });

  it('应该处理无效表达式', async () => {
    const result = await calculatorTool.execute({ expression: 'abc + 123' });
    expect(result).toContain('计算错误');
  });
});
```

### 运行测试，确保仍然通过

```bash
npm test

# 预期输出：所有测试 ✅
```

**重构的原则：**
- 不改变外部行为
- 提高代码可读性
- 减少代码重复
- 提高代码可维护性

---

## 4. VERIFY 阶段 - 完整验证

确保所有测试通过，且覆盖率达标。

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

## 完整示例循环

```
┌─────────────────────────────────────────────────────────────┐
│  1. RED    → 编写失败的测试，验证测试有效                    │
│     ↓                                                          │
│  2. GREEN  → 编写最小实现，刚好通过测试                        │
│     ↓                                                          │
│  3. REFACTOR → 在测试保护下优化代码                            │
│     ↓                                                          │
│  4. VERIFY  → 运行所有测试，确保没有破坏                       │
│     ↓                                                          │
│  5. 回到步骤 1（添加新功能或测试）                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 常见错误

### ❌ 错误做法 1：跳过 RED 阶段

直接写代码，然后补测试。

**问题**：
- 测试可能没有真正验证功能
- 容易写出"总是通过"的测试
- 失去了 TDD 的核心价值

### ❌ 错误做法 2：一次写太多代码

在 GREEN 阶段写了完整的实现，包含错误处理。

**问题**：
- 调试困难
- 不清楚是哪部分代码有问题
- 违反了"最小实现"原则

### ❌ 错误做法 3：重构时不运行测试

修改代码结构后忘记验证测试。

**问题**：
- 可能引入新 bug
- 破坏了原有功能
- 失去了测试的保护

---

## 最佳实践

### ✅ 保持小步快跑

- 每个循环只实现一个小功能
- 频繁运行测试（每 2-3 分钟）
- 不要积累太多未测试的代码

### ✅ 测试命名要清晰

```typescript
// 好的命名
it('当用户名为空时应该返回错误')
it('应该正确处理大数计算')

// 不好的命名
it('测试1')
it('功能测试')
```

### ✅ 一个测试只验证一件事

```typescript
// 好的做法
it('应该正确执行加法')
it('应该正确执行减法')
it('应该处理除零错误')

// 不好的做法
it('应该正确执行所有运算', () => {
  // 测试加法、减法、乘法、除法...
  // 太多内容，难以定位问题
})
```

---

## 参考资源

- [TDD 维基百科](https://en.wikipedia.org/wiki/Test-driven_development)
- [Vitest 官方文档](https://vitest.dev)
- [测试最佳实践](https://testingjavascript.com/)
