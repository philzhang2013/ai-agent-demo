# Demo 1: 命令行 AI Agent

> 理解 Agent 的核心工作循环

## 学习目标

通过这个 Demo，你将学习到：

1. **Agent 核心循环** - `用户输入 → LLM 思考 → 工具调用 → 结果处理 → 最终回答`
2. **工具系统** - 如何定义和注册工具
3. **消息历史管理** - 多轮对话的上下文维护
4. **思考过程可视化** - 理解 Agent 的决策过程

## 项目结构

```
01-cli-agent/
├── src/
│   └── index.ts      # 主程序
├── package.json
├── tsconfig.json
├── .env.example      # 环境变量示例
└── README.md
```

## 快速开始

### 1. 获取 API Key

访问 [智谱 AI 开放平台](https://open.bigmodel.cn/) 注册并获取 API Key。

### 2. 安装依赖

```bash
cd demos/01-cli-agent
npm install
# 或
pnpm install
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

### 4. 运行

```bash
npm run dev
```

## Agent 核心概念

### 1. Agent 循环

```
┌─────────────────────────────────────────┐
│              Agent 核心循环              │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────┐    ┌──────────┐          │
│  │ 用户输入  │───▶│ LLM 思考  │          │
│  └──────────┘    └────┬─────┘          │
│                       │                │
│                       ▼                │
│               ┌──────────────┐         │
│               │ 需要调用工具？│         │
│               └──────┬───────┘         │
│                      │                 │
│           ┌─────────┴─────────┐        │
│           ▼                   ▼        │
│        [是]                 [否]       │
│           │                   │        │
│           ▼                   ▼        │
│   ┌─────────────┐      ┌───────────┐  │
│   │ 执行工具     │      │ 返回答案   │  │
│   └──────┬──────┘      └───────────┘  │
│          │                            │
│          └──────▶ 回到 LLM 思考        │
│                                         │
└─────────────────────────────────────────┘
```

### 2. 工具定义

```typescript
interface Tool {
  name: string;          // 工具名称
  description: string;   // 工具描述（LLM 理解用）
  parameters: object;    // 参数 schema
  execute: (args) => string;  // 执行函数
}
```

### 3. 消息历史

```typescript
interface Message {
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  name?: string;  // tool 消息需要
}
```

## 示例对话

```
👤 你: 北京今天天气怎么样？然后帮我算一下 18 + 25 等于多少

🔄 [Agent 迭代 1]
📋 思考: 需要调用工具 "get_weather"
📝 参数: {"city":"北京"}
✅ 工具结果: 晴天，温度 18°C，空气质量良好

🔄 [Agent 迭代 2]
📋 思考: 需要调用工具 "calculator"
📝 参数: {"expression":"18 + 25"}
✅ 工具结果: 计算结果: 18 + 25 = 43

🔄 [Agent 迭代 3]

🤖 助手: 北京今天的天气是晴天，温度 18°C，空气质量良好。
另外，18 + 25 = 43。
```

## 关键代码解析

### Agent 类

```typescript
class Agent {
  private messages: Message[] = [];  // 消息历史

  async processUserInput(userInput: string): Promise<string> {
    // 1. 添加用户消息
    this.messages.push({ role: 'user', content: userInput });

    // 2. Agent 循环
    while (true) {
      // 调用 LLM
      const response = await this.callLLM();

      // 检查是否需要调用工具
      const toolCall = this.parseToolCall(response);

      if (toolCall) {
        // 执行工具，将结果加入消息历史
        const result = this.executeTool(toolCall.name, toolCall.args);
        this.messages.push({ role: 'tool', content: result });
        continue;  // 继续循环
      }

      // 返回最终答案
      return response;
    }
  }
}
```

## 练习建议

1. **添加新工具** - 尝试添加一个新工具（如：搜索、翻译）
2. **优化提示词** - 修改系统提示，观察 Agent 行为变化
3. **错误处理** - 添加更完善的错误处理逻辑

## 下一步

完成这个 Demo 后，继续学习 [Demo 2: Web 应用 Agent](../02-web-agent/)，学习如何将 Agent 集成到 Web 应用中。
