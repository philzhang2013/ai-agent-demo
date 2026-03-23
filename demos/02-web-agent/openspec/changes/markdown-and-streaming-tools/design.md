# 变更设计：Markdown 渲染 + 流式工具调用

**变更 ID**: `markdown-and-streaming-tools`
**状态**: 设计中
**最后更新**: 2026-03-23

---

## 架构设计

### 整体架构图

```
┌──────────────────────────────────────────────────────────────────┐
│                    前后端交互架构                                │
└──────────────────────────────────────────────────────────────────┘

用户输入 → 前端组件                                    后端处理
   │            │                                             │
   ▼            ▼                                             ▼
"计算18+25"   ┌─────────────┐                          ┌──────────────┐
             │ MessageList │                          │   SSE Stream │
             │             │                          │              │
             │ ┌─────────┐ │                          │ ┌──────────┐ │
             │ │Markdown │ │                          │ │ ZhipuAI │ │
             │ │Renderer │ │                          │ │ Client  │ │
             │ └────┬────┘ │                          │ └────┬─────┘ │
             └──────┼──────┘                          └──────┼───────┘
                    │                                        │
                    │ SSE 事件流                              │
                    ▼                                        ▼
              ┌─────────────────────────────────────────────────┐
              │              SSE 事件序列                       │
              ├─────────────────────────────────────────────────┤
              │ event: token → 累积文本 → Markdown 渲染        │
              │ event: tool_call → 显示"执行中"卡片            │
              │ event: tool_result → 显示结果                  │
              │ event: done → 完成                             │
              └─────────────────────────────────────────────────┘
```

---

## Phase 1: Markdown 渲染详细设计

### 1.1 组件层次结构

```
MessageList.vue
└── MessageContent
    ├── UserMessage (纯文本)
    └── AssistantMessage
        └── MarkdownRenderer.vue
            ├── 解析层 (marked)
            ├── 清理层 (DOMPurify)
            └── 渲染层 (highlight.js + 自定义样式)
```

### 1.2 数据流

```
message.content (Markdown 文本)
       │
       ▼
marked.parse() → HTML 字符串
       │
       ▼
addLineNumbers() → 增强 HTML（添加行号、复制按钮）
       │
       ▼
DOMPurify.sanitize() → 清理后的安全 HTML
       │
       ▼
v-html 渲染 → 最终显示
```

### 1.3 安全策略

**DOMPurify 配置**：
```typescript
const purifyConfig = {
  ALLOWED_TAGS: [
    'p', 'br', 'strong', 'em', 'code', 'pre', 'blockquote',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'a', 'table', 'thead', 'tbody', 'tr', 'td', 'th',
    'div', 'span', 'hr', 'img', 'button'
  ],
  ALLOWED_ATTR: ['href', 'class', 'id', 'style', 'data-*', 'src', 'alt', 'title', 'width', 'height'],
  ALLOW_DATA_ATTR: true,
}
```

---

## Phase 2: 流式工具调用详细设计

### 2.1 后端改造

#### 2.1.1 ZhipuClient.chat_stream() 改造

**当前签名**：
```python
async def chat_stream(self, model: str, messages, tools=None) -> AsyncIterator[str]
```

**新签名**：
```python
async def chat_stream(self, model: str, messages, tools=None) -> AsyncIterator[dict]
```

**返回格式**：
```python
# 文本 token
yield {"event": "token", "data": {"content": "让"}}

# 工具调用
yield {"event": "tool_call", "data": {"tool": "calculator", "args": {"expression": "18+25"}}}
```

#### 2.1.2 SSE 事件格式

```typescript
// token 事件（现有）
event: token
data: {"content": "让"}

// tool_call 事件（新增）
event: tool_call
data: {"tool": "calculator", "args": {"expression": "18+25"}}

// tool_result 事件（新增）
event: tool_result
data: {"tool": "calculator", "result": "计算结果: 18 + 25 = 43"}

// tool_error 事件（新增）
event: tool_error
data: {"tool": "calculator", "error": "表达式无效"}
```

### 2.2 前端改造

#### 2.2.1 类型定义扩展

```typescript
export interface SSEEvent {
  type: 'token' | 'tool_call' | 'tool_result' | 'tool_error' | 'done' | 'error'
  content?: string
  tool?: string
  args?: Record<string, any>
  result?: string
  error?: string
  session_id?: string
}

export interface ToolCall {
  id: string
  tool: string
  args: Record<string, any>
  status: 'executing' | 'success' | 'error'
  result?: string
  error?: string
  timestamp: number
}
```

#### 2.2.2 状态管理

```typescript
interface ChatState {
  messages: ChatMessage[]
  isLoading: boolean
  sessionId: string | null

  // 新增
  currentToolCalls: ToolCall[]
  isProcessingTool: boolean  // 工具执行期间禁用输入
}
```

#### 2.2.3 工具卡片组件

```vue
<template>
  <div :class="['tool-card', `tool-card-${status}`]">
    <div class="tool-header">
      <span class="tool-icon">{{ icon }}</span>
      <span class="tool-name">{{ toolName }}</span>
    </div>
    <div class="tool-args">
      <code>{{ formatArgs(args) }}</code>
    </div>
    <div v-if="result" class="tool-result">
      <MarkdownRenderer :content="result" />
    </div>
    <div v-if="status === 'executing'" class="tool-status">
      ⏳ 执行中...
    </div>
  </div>
</template>
```

---

## 数据模型

### 前端类型定义

```typescript
interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
}

interface ToolCall {
  id: string
  tool: string
  args: Record<string, any>
  status: 'executing' | 'success' | 'error'
  result?: string
  error?: string
  timestamp: number
}
```

---

## 错误处理

### 工具执行失败

**场景**：用户输入"计算 abc + 123"（无效表达式）

**处理流程**：
```
1. 后端检测 tool_call → calculator
2. 执行失败，捕获异常
3. 返回 tool_error 事件
4. 前端显示红色错误卡片
5. LLM 继续生成道歉或解释
```

---

## 性能考虑

### Markdown 渲染性能

**优化策略**：
1. 懒加载：代码块默认折叠
2. 防抖：流式输出时限制渲染频率

### 流式输出性能

**优化策略**：
1. 批量处理：每 50ms 批量更新一次 DOM
2. 节流：限制最多 10 次/秒 UI 更新

---

## 测试策略

### 单元测试

**后端**：
- `tests/test_zhipuai.py`: 测试 `chat_stream()` 返回字典格式
- `tests/test_agent.py`: 测试 `process_message_stream()` 工具调用逻辑

**前端**：
- `MarkdownRenderer.spec.ts`: ✅ 已完成（19 tests, 88.79% coverage）
- `MessageList.spec.ts`: ✅ 已完成（11 tests）
- `ToolCard.spec.ts`: 待创建

---

## 迁移计划

### 向后兼容

**非流式接口保留**：
- `POST /api/chat` 保持不变
- 流式改造不影响现有功能

**渐进式迁移**：
```
阶段 1: Markdown 渲染（当前实施）
  └─ 前端纯增量变更

阶段 2: 流式工具调用（后续）
  └─ 保留非流式接口作为后备
```
