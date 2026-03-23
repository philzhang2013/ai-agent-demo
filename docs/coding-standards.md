# 技术约定和代码规范

本文档说明项目中的技术约定和代码编写规范。

---

## 代码组织

### 文件大小

- **推荐**：200-400 行
- **上限**：800 行
- **超过时**：考虑拆分模块

```
好：
src/
├── calculator.ts      # 150 行
├── weather.ts         # 200 行
└── tools/
    ├── index.ts       # 50 行
    └── utils.ts       # 100 行

不好：
src/
└── tools.ts           # 1500 行 ⚠️ 过大
```

### 组织原则

- **高内聚**：相关功能放在一起
- **低耦合**：模块间依赖最小化
- **单一职责**：每个模块只做一件事

```typescript
// 好的设计：职责清晰
calculator.ts      # 计算器相关
weather.ts         # 天气相关
agent.ts           # Agent 核心
tools/
    ├── index.ts    # 工具导出
    └── utils.ts    # 通用工具

// 不好的设计：职责混乱
utils.ts           # 包含所有内容 ⚠️
```

### 类型安全

```typescript
// ✅ 好的做法：明确类型
interface CalculatorInput {
  expression: string;
}

interface CalculatorResult {
  result: number;
  error?: string;
}

function calculate(input: CalculatorInput): CalculatorResult {
  // ...
}

// ❌ 不好的做法：使用 any
function calculate(input: any): any {
  // ...
}
```

---

## 错误处理

### 显式处理

每层代码都应该处理错误，不要静默忽略。

```typescript
// ✅ 好的做法：显式处理
async function fetchUser(id: string) {
  try {
    const response = await api.getUser(id);
    return response.data;
  } catch (error) {
    logger.error(`获取用户失败: ${id}`, error);
    throw new UserNotFoundError(id);
  }
}

// ❌ 不好的做法：静默忽略
async function fetchUser(id: string) {
  try {
    const response = await api.getUser(id);
    return response.data;
  } catch (error) {
    // 什么都不做 ⚠️
  }
}
```

### 分层错误处理

```typescript
// API 层：面向用户的友好消息
try {
  await processRequest(request);
} catch (error) {
  if (error instanceof ValidationError) {
    return { error: '输入格式不正确' };
  }
  logger.error('处理请求失败', error);
  return { error: '服务暂时不可用，请稍后重试' };
}

// 服务层：详细日志
try {
  await businessLogic();
} catch (error) {
  logger.error('业务逻辑失败', {
    error: error.message,
    stack: error.stack,
    context: { userId, action }
  });
  throw error; // 继续向上抛出
}
```

### 错误类型

```typescript
// 定义业务错误类型
class ValidationError extends Error {
  constructor(field: string, value: unknown) {
    super(`验证失败: ${field} = ${value}`);
    this.name = 'ValidationError';
  }
}

class NotFoundError extends Error {
  constructor(resource: string, id: string) {
    super(`${resource} 不存在: ${id}`);
    this.name = 'NotFoundError';
  }
}

// 使用
if (!user) {
  throw new NotFoundError('用户', userId);
}
```

---

## 不可变性 (CRITICAL)

### 创建新对象，不修改原对象

```typescript
// ✅ 好的做法：返回新对象
function addItem(cart: Cart, item: Item): Cart {
  return {
    ...cart,
    items: [...cart.items, item]
  };
}

// ❌ 不好的做法：修改原对象
function addItem(cart: Cart, item: Item): Cart {
  cart.items.push(item);  // 修改了原对象 ⚠️
  return cart;
}
```

### 使用不可变数据结构

```typescript
// ✅ 使用 readonly
interface User {
  readonly id: string;
  readonly name: string;
  readonly createdAt: Date;
}

// ✅ 使用 const 断言
const TOOLS = [
  { name: 'calculator', execute: () => {} },
  { name: 'weather', execute: () => {} }
] as const;

// ❌ 避免可变默认参数
function dangerous(options = { cache: true }) {
  options.cache = false;  // 修改了默认对象 ⚠️
}

// ✅ 使用解构创建新对象
function safe(options: { cache?: boolean } = {}) {
  const config = { cache: true, ...options };
}
```

### 数组操作

```typescript
// ✅ 不修改原数组
const newItems = [...items, newItem];          // 添加
const filtered = items.filter(item => ...);    // 过滤
const mapped = items.map(item => ...);         // 转换
const found = items.find(item => ...);         // 查找

// ❌ 修改原数组
items.push(newItem);                           // 添加 ⚠️
items.splice(0, 1);                            // 删除 ⚠️
items.sort((a, b) => ...);                     // 排序 ⚠️
```

---

## 函数设计

### 纯函数优先

```typescript
// ✅ 纯函数：无副作用
function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// ❌ 非纯函数：有副作用
function calculateTotal(items: Item[]): number {
  total++; // 修改外部变量 ⚠️
  console.log('计算中...'); // 副作用 ⚠️
  return items.reduce((sum, item) => sum + item.price, 0);
}
```

### 函数长度

```typescript
// ✅ 好的做法：短小精悍
function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// ❌ 不好的做法：过长
function calculateTotal(items: Item[]): number {
  // 100+ 行代码...
  // 难以理解和维护
}
```

### 参数数量

```typescript
// ✅ 好的做法：参数少于 4 个
function createUser(name: string, email: string): User { }

// ✅ 多参数时使用对象
function createUser(options: {
  name: string;
  email: string;
  age?: number;
  address?: string;
}): User { }

// ❌ 不好的做法：参数过多
function createUser(
  name: string,
  email: string,
  age: number,
  address: string,
  phone: string,
  role: string
): User { }
```

---

## 命名规范

### 变量命名

```typescript
// ✅ 好的命名：清晰、描述性
const userCount = 10;
const isAuthenticated = true;
const maxRetries = 3;

// ❌ 不好的命名：模糊、不清晰
const n = 10;
const flag = true;
const num = 3;
```

### 函数命名

```typescript
// ✅ 使用动词开头
function getUser() { }
function calculateTotal() { }
function isValid() { }

// ❌ 避免无意义命名
function doIt() { }
function process() { }
function handle() { }
```

### 布尔值命名

```typescript
// ✅ 使用 is/has/should 前缀
const isActive = true;
const hasPermission = false;
const shouldUpdate = true;

// ❌ 避免否定命名
const isInactive = true;  // 双重否定 ⚠️
```

---

## 注释规范

### 何时需要注释

```typescript
// ✅ 需要：解释"为什么"（业务逻辑）
// 使用递归而不是循环，因为树深度不确定
function traverseTree(node: Node) { }

// ✅ 需要：解释复杂算法
// 使用 KMP 算法进行字符串匹配
function search(text: string, pattern: string) { }

// ❌ 不需要：重复代码本身
// 设置用户名为 name
user.name = name;
```

### JSDoc 注释

```typescript
/**
 * 计算购物车总价
 * @param items - 购物车商品列表
 * @param discount - 折扣比例（0-1）
 * @returns 总价（保留 2 位小数）
 * @throws {Error} 当折扣比例无效时抛出错误
 */
function calculateTotal(
  items: Item[],
  discount: number
): number {
  // ...
}
```

---

## TypeScript 配置

```json
{
  "compilerOptions": {
    "strict": true,           // 启用严格模式
    "noImplicitAny": true,    // 禁止隐式 any
    "strictNullChecks": true, // 严格空值检查
    "noUnusedLocals": true,   // 检查未使用的变量
    "noUnusedParameters": true, // 检查未使用的参数
    "noImplicitReturns": true, // 检查是否有返回值
    "forceConsistentCasingInFileNames": true // 文件名大小写敏感
  }
}
```

---

## 参考资源

- [TypeScript 最佳实践](https://typescript-eslint.io/rules/)
- [Clean Code 原则](https://github.com/ryanmcdermott/clean-code-javascript)
