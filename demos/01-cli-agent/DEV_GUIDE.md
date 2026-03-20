# Demo 1: 命令行 AI Agent - 开发文档

## 目录

1. [项目概述](#项目概述)
2. [核心概念](#核心概念)
3. [架构设计](#架构设计)
4. [代码实现](#代码实现)
5. [工作流程](#工作流程)
6. [多提供商支持](#多提供商支持)
7. [测试指南](#测试指南)

---

## 项目概述

### 学习目标

本 Demo 通过构建一个命令行 AI Agent，帮助理解 **Agent 核心工作循环**：

```
用户输入 → LLM 思考 → 工具调用 → 结果处理 → 最终回复
```

### 功能特性

- ✅ **工具调用**: 计算器、天气查询
- ✅ **多轮对话**: 维护对话历史
- ✅ **多提供商支持**: 智谱 AI、MiniMax、Kimi
- ✅ **模拟模式**: 无需消耗 API 即可测试

### 技术栈

- **语言**: TypeScript
- **运行时**: Node.js
- **LLM 提供商**: 智谱 AI / MiniMax / Kimi (Moonshot)
- **测试框架**: Vitest

---

## 核心概念

### 什么是 AI Agent？

**AI Agent** 是能够感知环境、进行推理，并采取行动以实现目标的智能体。

```
┌─────────────────────────────────────────────────────────┐
│                    AI Agent 循环                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────┐      ┌─────────┐      ┌─────────┐       │
│  │ 用户输入 │ ───> │ LLM 推理 │ ───> │ 判断行动 │       │
│  └─────────┘      └─────────┘      └─────────┘       │
│       �                                  │             │
│       │                         ┌──────┴──────┐       │
│       │                         │             │       │
│       ▼                         ▼             ▼       │
│  ┌─────────┐              ┌─────────┐  ┌─────────┐  │
│  │ 需要工具 │ ─── Yes ──> │ 调用工具 │  │ 直接回复 │  │
│  └─────────┘              └─────────┘  └─────────┘  │
│       │ No                       │             │       │
│       └──────────────────────────┴─────────────┘     │
│                                  │                   │
│                                  ▼                   │
│                         ┌─────────────┐             │
│                         │ 更新对话历史 │             │
│                         └─────────────┘             │
└─────────────────────────────────────────────────────────┘
```

### Agent vs 传统 LLM

| 特性 | 传统 LLM | AI Agent |
|------|----------|----------|
| 输入处理 | 仅理解文本 | 理解 + 决策 |
| 能力范围 | 固定知识 | 可扩展工具 |
| 交互方式 | 单次问答 | 循环迭代 |
| 实际行动 | 无 | 可调用外部 API |

---

## 架构设计

### 目录结构

```
01-cli-agent/
├── src/
│   ├── agent.ts           # Agent 核心类
│   ├── index.ts           # 程序入口
│   ├── tools.ts           # 工具定义
│   ├── types.ts           # 类型定义
│   ├── test-api.ts        # API 测试
│   └── providers/         # LLM 提供商适配器
│       ├── index.ts       # 工厂函数
│       ├── base.ts        # 基础接口
│       ├── zhipuai.ts     # 智谱 AI
│       ├── minimax.ts     # MiniMax
│       ├── kimi.ts        # Kimi
│       └── ...
├── tests/                 # 测试文件
├── dist/                  # 编译输出
├── .env                   # 环境变量
├── package.json
└── vitest.config.ts
```

### 设计模式

#### 1. 适配器模式 (Adapter Pattern)

为不同 LLM 提供商提供统一接口：

```
┌──────────────────────────────────────────────────────┐
│                   Agent 类                            │
│  ┌────────────────────────────────────────────────┐  │
│  │         client: LLMClient (interface)          │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
   ┌──────────┐    ┌──────────┐    ┌──────────┐
   │ZhipuClient│    │MinimaxClient│  │KimiClient │
   └──────────┘    └──────────┘    └──────────┘
```

#### 2. 工厂模式 (Factory Pattern)

统一创建客户端实例：

```typescript
export function createClient(
  provider: LLMProvider,
  apiKey: string,
  baseURL?: string
): LLMClient {
  switch (provider) {
    case LLMProvider.ZHIPUAI:
      return new ZhipuClient(apiKey, baseURL);
    case LLMProvider.MINIMAX:
      return new MinimaxClient(apiKey, baseURL);
    case LLMProvider.KIMI:
      return new KimiClient(apiKey, baseURL);
  }
}
```

---

## 代码实现

### 1. Agent 类 (src/agent.ts)

#### 核心属性

```typescript
export class Agent {
  private client: LLMClient | null;      // LLM 客户端
  private messages: Message[];            // 对话历史
  private maxIterations: number;          // 最大迭代次数
  private iterationCount: number;         // 当前迭代计数
  private mockMode: boolean;              // 模拟模式标志
  private provider: LLMProvider;          // LLM 提供商
  private model: string;                  // 模型名称
}
```

#### 系统提示词

```typescript
private getSystemPrompt(): string {
  return `你是一个智能 AI 助手，可以帮助用户回答问题并使用工具完成任务。

可用的工具:
- calculator: 执行数学计算
- get_weather: 查询指定城市的天气信息

当需要使用工具时，请按以下格式返回:
TOOL_CALL: <工具名称>
ARGUMENTS: <JSON 格式的参数>

例如:
TOOL_CALL: calculator
ARGUMENTS: {"expression": "18 + 25"}

工具调用结果会自动添加到对话中，请根据结果给用户一个友好的回复。`;
}
```

**为什么需要系统提示词？**

- **定义能力边界**: 告诉 LLM 它能做什么
- **规范输出格式**: 统一的工具调用格式
- **引导行为**: 如何处理工具结果

#### 工具调用解析

```typescript
private parseToolCall(content: string): ToolCall | null {
  const toolCallMatch = content.match(/TOOL_CALL:\\s*(\\w+)/);
  const argsMatch = content.match(/ARGUMENTS:\\s*(\\{.*\\})/);

  if (toolCallMatch && argsMatch) {
    try {
      return {
        name: toolCallMatch[1],
        arguments: JSON.parse(argsMatch[1])
      };
    } catch {
      return null;
    }
  }
  return null;
}
```

**工作原理**：
1. 使用正则表达式提取工具名称
2. 解析 JSON 格式的参数
3. 返回结构化数据供执行使用

#### 核心循环

```typescript
async processUserInput(userInput: string): Promise<string> {
  this.messages.push({ role: 'user', content: userInput });

  while (this.iterationCount < this.maxIterations) {
    this.iterationCount++;

    // 1. 调用 LLM
    const response = await this.callLLM();

    // 2. 检查是否需要调用工具
    const toolCall = this.parseToolCall(response);

    if (toolCall) {
      // 3. 执行工具
      const result = await this.executeTool(
        toolCall.name,
        toolCall.arguments
      );

      // 4. 添加工具结果到对话历史
      this.messages.push({ role: 'assistant', content: response });
      this.messages.push({
        role: 'function',
        content: result,
        name: toolCall.name
      });

      continue; // 继续循环，让 LLM 基于结果生成最终回复
    }

    // 5. 返回最终回复
    return response;
  }

  return '达到最大迭代次数，请重新尝试。';
}
```

**流程图**：

```
┌─────────────────────────────────────────────────────────┐
│                  processUserInput                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 添加用户消息到历史                                   │
│     │                                                    │
│     ▼                                                    │
│  2. 开始循环 (maxIterations 限制)                        │
│     │                                                    │
│     ▼                                                    │
│  3. 调用 LLM 获取响应                                    │
│     │                                                    │
│     ├────────────────────────────────┐                  │
│     │                                │                  │
│     ▼                                ▼                  │
│  解析到工具调用?                     否                  │
│     │ Yes                                                │
│     ▼                                                    │
│  4. 执行工具                                            │
│     │                                                    │
│     ▼                                                    │
│  5. 添加工具结果到历史                                   │
│     │                                                    │
│     └──────────> 继续循环（回到步骤 3）                  │
│                                                     │    │
│                                                     ▼    │
│                                              返回响应    │
└─────────────────────────────────────────────────────────┘
```

### 2. 工具系统 (src/tools.ts)

#### 工具接口定义

```typescript
export interface Tool {
  name: string;                    // 工具名称
  description: string;             // 工具描述
  parameters: {                    // 参数定义
    type: string;
    properties: Record<string, any>;
    required?: string[];
  };
  execute: (args: Record<string, any>) => Promise<string> | string;
}
```

#### 计算器工具实现

```typescript
export const calculatorTool: Tool = {
  name: 'calculator',
  description: '执行数学计算，支持加减乘除和括号',

  parameters: {
    type: 'object',
    properties: {
      expression: {
        type: 'string',
        description: '要计算的数学表达式'
      }
    },
    required: ['expression']
  },

  execute: (args) => {
    try {
      const expression = args.expression.trim();
      // 使用 Function 构造器安全计算
      const result = Function('"use strict"; return (' + expression + ')')();
      return `计算结果: ${expression} = ${result}`;
    } catch (error) {
      return `计算错误: ${error}`;
    }
  }
};
```

#### 天气工具实现

```typescript
const weatherData: Record<string, WeatherInfo> = {
  '北京': { condition: '晴天', temperature: 18, aqi: 75 },
  '上海': { condition: '多云', temperature: 22, aqi: 60 },
  '深圳': { condition: '阴天', temperature: 25, aqi: 45 },
  '广州': { condition: '小雨', temperature: 24, aqi: 55 },
};

export const weatherTool: Tool = {
  name: 'get_weather',
  description: '查询指定城市的天气信息',

  parameters: {
    type: 'object',
    properties: {
      city: {
        type: 'string',
        description: '城市名称'
      }
    },
    required: ['city']
  },

  execute: (args) => {
    const data = weatherData[args.city] || {
      condition: '未知',
      temperature: '--',
      aqi: '--'
    };
    return `${args.city}今天${data.condition}，温度 ${data.temperature}°C，空气质量 ${data.aqi}`;
  }
};
```

### 3. LLM 提供商适配器

#### 基础接口 (src/providers/base.ts)

```typescript
export interface LLMClient {
  chat(params: ChatParams): Promise<ChatResponse>;
}

export interface ChatParams {
  model: string;
  messages: (Message | ToolMessage)[];
  stream?: boolean;
}

export interface ChatResponse {
  content: string;
  usage?: TokenUsage;
}
```

#### 智谱 AI 适配器 (src/providers/zhipuai.ts)

```typescript
export class ZhipuClient implements LLMClient {
  private apiKey: string;
  private baseURL: string;

  constructor(apiKey: string, baseURL?: string) {
    this.apiKey = apiKey;
    this.baseURL = baseURL || 'https://open.bigmodel.cn/api/coding/paas/v4';
  }

  async chat(params: ChatParams): Promise<ChatResponse> {
    const url = `${this.baseURL}/chat/completions`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({
        model: params.model,
        messages: params.messages,
        stream: false
      })
    });

    const data = await response.json();
    return {
      content: data.choices[0]?.message?.content || '',
      usage: data.usage
    };
  }
}
```

---

## 工作流程

### 完整执行流程示例

用户输入: **"北京天气"**

```
步骤 1: 用户输入
┌─────────────────────────────────┐
│ 用户: 北京天气                   │
└─────────────────────────────────┘
              │
              ▼
步骤 2: 添加到消息历史
┌─────────────────────────────────┐
│ messages = [                    │
│   { role: 'system', ... },      │
│   { role: 'user',               │
│     content: '北京天气' }        │
│ ]                               │
└─────────────────────────────────┘
              │
              ▼
步骤 3: 调用 LLM
┌─────────────────────────────────┐
│ 发送到智谱 AI:                  │
│ - 模型: glm-5                   │
│ - 消息历史                       │
│ - 系统提示词（包含工具说明）     │
└─────────────────────────────────┘
              │
              ▼
步骤 4: LLM 响应
┌─────────────────────────────────┐
│ LLM 返回:                       │
│ TOOL_CALL: get_weather          │
│ ARGUMENTS: {"city": "北京"}     │
└─────────────────────────────────┘
              │
              ▼
步骤 5: 解析工具调用
┌─────────────────────────────────┐
│ 解析结果:                       │
│ - name: "get_weather"           │
│ - arguments: {city: "北京"}      │
└─────────────────────────────────┘
              │
              ▼
步骤 6: 执行工具
┌─────────────────────────────────┐
│ 调用 weatherTool.execute():     │
│ 输入: {city: "北京"}             │
│ 输出: "北京今天晴天，温度 18°C"  │
└─────────────────────────────────┘
              │
              ▼
步骤 7: 添加工具结果
┌─────────────────────────────────┐
│ messages.push({                 │
│   role: 'assistant',            │
│   content: 'TOOL_CALL: ...'     │
│ })                              │
│ messages.push({                 │
│   role: 'function',             │
│   name: 'get_weather',          │
│   content: '北京今天晴天...'    │
│ })                              │
└─────────────────────────────────┘
              │
              ▼
步骤 8: 再次调用 LLM
┌─────────────────────────────────┐
│ 发送到智谱 AI:                  │
│ 包含工具调用结果                 │
└─────────────────────────────────┘
              │
              ▼
步骤 9: 最终回复
┌─────────────────────────────────┐
│ 🤖 助手: 根据查询结果，          │
│ 北京今天的天气情况如下：         │
│ 🌞 天气状况：晴天               │
│ 🌡️ 温度：18°C                  │
└─────────────────────────────────┘
```

---

## 多提供商支持

### 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                      Agent 类                            │
│                                                          │
│  provider: LLMProvider (enum)                           │
│  ┌────────────────────────────────────────────────┐     │
│  │ ZHIPUAI = 'zhipuai'                            │     │
│  │ MINIMAX = 'minimax'                            │     │
│  │ KIMI = 'kimi'                                  │     │
│  └────────────────────────────────────────────────┘     │
│                          │                              │
│                          ▼                              │
│  ┌────────────────────────────────────────────────┐     │
│  │     createClient(provider, apiKey, baseURL)    │     │
│  └────────────────────────────────────────────────┘     │
│                          │                              │
│         ┌────────────────┼────────────────┐             │
│         ▼                ▼                ▼             │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐       │
│   │ 智谱 AI  │     │ MiniMax  │     │   Kimi   │       │
│   │ glm-5    │     │  M2-her  │     │ moonshot │       │
│   └──────────┘     └──────────┘     └──────────┘       │
└─────────────────────────────────────────────────────────┘
```

### 环境变量配置

```bash
# .env 文件

# 选择提供商
LLM_PROVIDER=zhipuai  # 或 minimax, kimi

# API Keys
ZHIPUAI_API_KEY=your_key
MINIMAX_API_KEY=your_key
KIMI_API_KEY=your_key

# 模型配置（可选）
ZHIPUAI_MODEL=glm-5
MINIMAX_MODEL=M2-her
KIMI_MODEL=moonshot-v1-8k

# 端点配置（可选）
ZHIPUAI_BASE_URL=https://open.bigmodel.cn/api/coding/paas/v4
```

### CodePlan 支持

**智谱 AI CodePlan**: 专门的编程套餐，使用专用端点

```typescript
// 默认使用 CodePlan 端点
const baseURL = process.env.ZHIPUAI_BASE_URL ||
  'https://open.bigmodel.cn/api/coding/paas/v4';
```

**MiniMax CodePlan**: OpenAI 兼容端点

```typescript
// MiniMax 使用 OpenAI 兼容格式
const url = `${this.baseURL}/v1/chat/completions`;
```

---

## 测试指南

### 单元测试

运行所有测试：

```bash
npm test
```

查看覆盖率：

```bash
npm run test:coverage
```

### API 测试

测试智谱 AI：

```bash
npm run test:api:zhipuai
```

测试 MiniMax：

```bash
npm run test:api:minimax
```

测试 Kimi：

```bash
npm run test:api:kimi
```

### 集成测试

启动智能体：

```bash
npm run dev
```

测试对话：

```
👤 你: 计算 18 + 25
🤖 助手: 计算结果是 43

👤 你: 北京天气
🤖 助手: 北京今天晴天，温度 18°C
```

### 模拟模式

无需消耗 API：

```bash
npm run dev:mock
```

---

## 关键学习点

### 1. 理解 Agent 循环

Agent 的核心是 **感知-推理-行动** 循环：

1. **感知**: 接收用户输入
2. **推理**: LLM 分析需要做什么
3. **决策**: 判断是否需要工具
4. **行动**: 调用工具或直接回复
5. **反馈**: 将结果加入历史，继续循环

### 2. 提示词工程

好的系统提示词是 Agent 成功的关键：

- ✅ 明确角色定位
- ✅ 列出可用工具
- ✅ 规范输出格式
- ✅ 引导回复风格

### 3. 迭代限制

设置 `maxIterations` 防止无限循环：

```typescript
while (this.iterationCount < this.maxIterations) {
  // ...
  this.iterationCount++;
}
```

### 4. 错误处理

每层都要处理错误：

```typescript
try {
  const result = await tool.execute(args);
} catch (error) {
  return `工具执行错误: ${error.message}`;
}
```

---

## 进阶方向

完成本 Demo 后，可以继续学习：

1. **Demo 2**: Web 应用 Agent - 学习流式输出
2. **Demo 3**: 聊天机器人 - 掌握多轮对话管理
3. **Demo 4**: 自动化工具 Agent - 实现复杂工具链

---

## 参考资料

- [智谱 AI 文档](https://open.bigmodel.cn/)
- [MiniMax 文档](https://platform.minimaxi.com/)
- [Kimi 文档](https://platform.moonshot.cn/)
- [Vitest 文档](https://vitest.dev/)
