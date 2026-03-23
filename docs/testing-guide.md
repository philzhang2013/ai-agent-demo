# 测试类型和规范

本文档说明项目中使用的测试类型及其编写规范。

---

## 测试类型

### 1. 单元测试 (Unit Tests)

**MANDATORY** - 每个函数/类都需要单元测试。

测试单个函数、方法或类的行为，隔离外部依赖。

```typescript
describe('工具函数', () => {
  describe('calculator', () => {
    it('应该执行加法', async () => {
      const result = await calculator({ expression: '1 + 2' });
      expect(result).toBe('3');
    });

    it('应该执行减法', async () => {
      const result = await calculator({ expression: '5 - 3' });
      expect(result).toBe('2');
    });

    it('应该处理错误输入', async () => {
      const result = await calculator({ expression: 'invalid' });
      expect(result).toContain('错误');
    });
  });
});
```

**单元测试原则**：
- 快速运行（毫秒级）
- 隔离外部依赖（使用 mock）
- 覆盖正常和异常情况
- 一个测试只验证一个功能点

---

### 2. 集成测试 (Integration Tests)

测试多个组件协作时的行为。

```typescript
describe('Agent 集成测试', () => {
  it('应该完成完整的工具调用流程', async () => {
    const agent = new Agent({ mockMode: true });
    const response = await agent.processUserInput('计算 18 + 25');
    expect(response).toContain('43');
  });

  it('应该处理多轮对话', async () => {
    const agent = new Agent({ mockMode: true });
    await agent.processUserInput('我的名字是小明');
    const response = await agent.processUserInput('我叫什么名字？');
    expect(response).toContain('小明');
  });
});
```

**集成测试原则**：
- 测试组件之间的交互
- 使用真实依赖（或接近真实的 mock）
- 关注业务流程而非实现细节
- 比单元测试慢，但比 E2E 快

---

### 3. E2E 测试 (End-to-End Tests)

测试完整的用户流程，模拟真实用户操作。

```typescript
describe('用户流程', () => {
  it('应该完成天气查询', async () => {
    // 打开页面
    await page.goto('http://localhost:5173');
    // 输入消息
    await page.fill('[data-test="chat-input"]', '北京今天天气怎么样？');
    // 发送消息
    await page.click('[data-test="send-button"]');
    // 验证回复
    await page.waitForSelector('[data-test="assistant-message"]');
    const message = await page.textContent('[data-test="assistant-message"]');
    expect(message).toContain('天气');
  });

  it('应该处理连续对话', async () => {
    await page.goto('http://localhost:5173');

    // 第一轮对话
    await page.fill('[data-test="chat-input"]', '我的名字是小明');
    await page.click('[data-test="send-button"]');
    await page.waitForSelector('[data-test="assistant-message"]');

    // 第二轮对话
    await page.fill('[data-test="chat-input"]', '我叫什么名字？');
    await page.click('[data-test="send-button"]');
    await page.waitForSelector('[data-test="assistant-message"]');

    // 验证记忆
    const message = await page.textContent('[data-test="assistant-message"]');
    expect(message).toContain('小明');
  });
});
```

**E2E 测试原则**：
- 测试关键用户流程
- 模拟真实用户操作
- 不频繁改动（维护成本高）
- 使用有意义的测试数据

---

## 测试金字塔

```
        /\
       /  \        E2E 测试（少量）
      /____\       - 关键用户流程
     /      \      - 最慢、最脆弱
    /        \
   /  集成测试  \    - 组件交互
  /______________\  - 中等速度
 /                \
/    单元测试      \  - 最多
/__________________\  - 最快、最可靠
```

**推荐比例**：
- 单元测试：70%
- 集成测试：20%
- E2E 测试：10%

---

## 测试命名规范

### describe 块

```typescript
// 使用描述性名称
describe('用户认证', () => {
  describe('登录功能', () => {
    describe('密码验证', () => {
      // ...
    });
  });
});

// 避免无意义名称
describe('Tests', () => { }); // ❌
describe('测试', () => { });   // ❌
```

### it 测试用例

```typescript
// 好的命名：描述清楚输入和期望
it('当密码正确时应该返回 Token')
it('当用户名为空时应该返回 400 错误')
it('应该处理网络超时情况')

// 不好的命名
it('测试登录')        // ❌ 太笼统
it('test1')          // ❌ 无意义
it('登录功能测试')    // ❌ 没说明期望
```

---

## AAA 模式

每个测试用例遵循 AAA 模式：

```typescript
it('应该正确计算总价', () => {
  // Arrange (准备)：设置测试数据
  const cart = new Cart();
  cart.addItem({ name: '苹果', price: 5, quantity: 3 });

  // Act (执行)：调用被测试的功能
  const total = cart.calculateTotal();

  // Assert (断言)：验证结果
  expect(total).toBe(15);
});
```

---

## Mock 和 Stub

### 使用 Mock 隔离外部依赖

```typescript
import { vi } from 'vitest';

describe('API 调用测试', () => {
  it('应该正确处理 API 响应', async () => {
    // Mock fetch 函数
    global.fetch = vi.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({ data: 'mock data' })
      })
    );

    // 执行测试
    const result = await fetchData();

    // 验证
    expect(result).toEqual({ data: 'mock data' });
    expect(fetch).toHaveBeenCalledTimes(1);
  });
});
```

---

## 异步测试

### 处理 Promise

```typescript
// 方式 1：使用 async/await
it('应该异步获取数据', async () => {
  const result = await fetchData();
  expect(result).toBe('data');
});

// 方式 2：返回 Promise
it('应该异步获取数据', () => {
  return fetchData().then(result => {
    expect(result).toBe('data');
  });
});
```

### 处理超时

```typescript
it('应该在超时前返回', async () => {
  // 增加超时时间（默认 5000ms）
  vi.setConfig({ testTimeout: 10000 });

  const result = await slowOperation();
  expect(result).toBe('done');
}, 10000); // 或作为参数传递
```

---

## 跳过和只运行特定测试

```typescript
describe('登录功能', () => {
  it('应该验证密码', () => {
    // 正常测试
  });

  // 跳过这个测试
  it.skip('应该发送验证邮件', () => {
    // TODO: 邮件服务未就绪
  });

  // 只运行这个测试
  it.only('应该处理登录失败', () => {
    // 调试时使用
  });
});
```

---

## 参考资源

- [Vitest 官方文档](https://vitest.dev)
- [Testing Library](https://testing-library.com/)
- [Playwright 文档](https://playwright.dev)
