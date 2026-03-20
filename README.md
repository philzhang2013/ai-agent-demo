# AI Agent 开发学习项目

> 这是一个 AI Agent 的学习项目，用于系统性地学习和实践 AI Agent 开发。

## 学习路径

### 第一阶段：基础准备（1-2天）

| 模块 | 内容 | 资源 |
|------|------|------|
| **LLM API 基础** | OpenAI API / Claude API 调用方式 | 官方文档 |
| **Agent 核心概念** | ReAct、Tool Use、Memory、Planning | 论文 + 博客 |
| **框架选择** | LangChain.js / AI SDK / LlamaIndex | 官方文档 |

### 第二阶段：四个递进 Demo（2-3周）

```
Demo 1: 命令行 Agent        →  理解 Agent 核心循环
Demo 2: Web 应用 Agent      →  学会流式输出 + 前端集成
Demo 3: 聊天机器人          →  掌握多轮对话 + 记忆管理
Demo 4: 自动化工具 Agent    →  实现工具调用 + 自主决策
```

### 第三阶段：进阶主题（后续）

- Multi-Agent 系统
- RAG + Agent 结合
- Agent 评测与优化
- 生产环境部署

---

## Demo 项目

### Demo 1：命令行 AI Agent

**目标**：理解 Agent 的核心工作循环

**功能**：
- 命令行问答
- 支持工具调用（如：查询天气、计算器、搜索）
- 显示思考过程

**技术栈**：
- TypeScript
- OpenAI API / Claude API
- Vercel AI SDK

---

## 技术栈

- **语言**：TypeScript / JavaScript
- **LLM 提供商**：OpenAI / Claude
- **Agent 框架**：Vercel AI SDK / LangChain.js
- **包管理器**：pnpm / bun

---

## 项目结构

```
ai-agent-demo/
├── demos/
│   ├── 01-cli-agent/       # 命令行 Agent
│   ├── 02-web-agent/       # Web 应用 Agent
│   ├── 03-chatbot/         # 聊天机器人
│   └── 04-automation/      # 自动化工具 Agent
├── docs/                   # 学习笔记
└── README.md
```

---

## 开始学习

每个 Demo 目录下都有独立的 README 和代码，可以按顺序学习。

---

## 参考资料

- [OpenAI API 文档](https://platform.openai.com/docs)
- [Claude API 文档](https://docs.anthropic.com)
- [Vercel AI SDK](https://sdk.vercel.ai)
- [LangChain.js](https://js.langchain.com)
