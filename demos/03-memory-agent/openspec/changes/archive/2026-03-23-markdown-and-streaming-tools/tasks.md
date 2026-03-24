# 实施任务清单

**变更**: markdown-and-streaming-tools
**状态**: Phase 1 实施中
**创建时间**: 2026-03-23

---

## Phase 1: Markdown 渲染

### 1.1 添加依赖 ✅

- [x] 在 `frontend/package.json` 添加依赖：
  - `marked: ^12.0.0`
  - `dompurify: ^3.0.6`
  - `highlight.js: ^11.9.0`
  - `@types/dompurify: ^3.0.5`
  - `jsdom: ^29.0.1`
  - `@vitest/coverage-v8: ^1.6.1`
- [x] 运行 `npm install` 安装依赖
- [x] 更新 `vite.config.ts` 添加 vitest 配置

**验证**: `npm list marked dompurify highlight.js` 显示已安装

---

### 1.2 创建 MarkdownRenderer.vue 组件 ✅

**文件**: `frontend/src/components/MarkdownRenderer.vue`

- [x] 创建组件，使用 `marked` 解析 Markdown
- [x] 使用 `DOMPurify` 清理 XSS
- [x] 使用 `highlight.js` 添加代码高亮
- [x] 实现行号显示功能
- [x] 实现复制按钮功能
- [x] 添加 scoped 样式

**测试**:
- [x] 创建 `frontend/src/components/__tests__/MarkdownRenderer.spec.ts`
- [x] 测试基本 Markdown 渲染
- [x] 测试代码块渲染和语法高亮
- [x] 测试 XSS 防护
- [x] 测试复制按钮功能
- [x] 测试响应式更新
- [x] 测试边界情况
- [x] 运行测试确保通过 (19 tests passed)
- [x] 验证覆盖率 ≥ 80% (88.79%)

**验证**: `npm test -- MarkdownRenderer.spec.ts --run` ✅

---

### 1.3 集成到 MessageList.vue ✅

**文件**: `frontend/src/components/MessageList.vue`

- [x] 导入 `MarkdownRenderer` 组件
- [x] 替换助手消息的纯文本显示为 `<MarkdownRenderer>`
- [x] 保持用户消息为纯文本
- [x] 创建 `MessageList.spec.ts` 单元测试
- [x] 测试 MarkdownRenderer 集成
- [x] 测试用户/助手消息区分
- [x] 测试加载状态和空状态
- [x] 运行测试确保通过 (11 tests passed)
- [x] 验证覆盖率 ≥ 80% (97.08%)

**验证**:
```bash
npm test -- MessageList.spec.ts --run ✅
npm run dev
# 在浏览器中测试发送包含 Markdown 的消息
```

---

### 1.4 Phase 1 验收 ✅

- [x] 所有单元测试通过 (30 tests: MarkdownRenderer 19 + MessageList 11)
- [x] 测试覆盖率 ≥ 80% (MarkdownRenderer 88.79%, MessageList 97.08%)
- [ ] 手动测试（需要用户验证）：
  - [ ] 发送消息包含 `# 标题`
  - [ ] 发送消息包含 `**粗体**` 和 `*斜体*`
  - [ ] 发送消息包含代码块，验证：
    - [ ] 语法高亮正确
    - [ ] 行号显示
    - [ ] 复制按钮可用
  - [ ] 发送消息包含链接，验证可点击
  - [ ] 发送 XSS 攻击尝试，验证被过滤

---

## Phase 1.5: 思维链显示 (Reasoning Content)

**背景**: 参考 GLM API 的 `reasoning_content` 字段，实现类似 DeepSeek 的思维链显示。

**需求**:
- 模型思考过程（`reasoning_content`）用灰色、较小字体显示
- 最终答案（`content`）用现有样式显示
- 支持 Preserved Thinking（多轮对话中保持历史 reasoning_content）

### 1.5.1 后端流式处理改造（思维链分离） ✅

**文件**: `backend/app/providers/zhipuai.py`

- [x] 修改 `chat_stream()` 返回类型为 `AsyncIterator[dict]`
- [x] 区分 `reasoning_content` 和 `content` 事件
- [x] 返回 `{"event": "reasoning", "content": "..."}`
- [x] 返回 `{"event": "content", "content": "..."}`
- [x] 启用 `thinking.type: "enabled"` 参数（GLM-4.5+ 模型）

**验证**:
```bash
# 检查返回的流包含 reasoning 和 content 事件
```

---

### 1.5.2 前端类型定义 ✅

**文件**: `frontend/src/api/types.ts`

- [x] 扩展 `ChatMessage` 接口：
  ```typescript
  interface ChatMessage {
    // ...
    reasoningContent?: string  // 思维链内容
  }
  ```
- [x] 扩展 `SSEEvent` 类型：
  ```typescript
  type: 'token' | 'reasoning' | 'content' | ...
  ```

---

### 1.5.3 前端状态管理 ✅

**文件**: `frontend/src/stores/chat.ts`

- [x] 添加 `reasoningBuffer: string` 用于累积思维链内容
- [x] 修改 `addMessage()` 支持分离 reasoning 和 content
- [x] 添加 `updateLastAssistantReasoning()` 方法
- [x] 添加 `appendToReasoningBuffer()` 方法
- [x] 在 `setLoading(true)` 时清空 reasoningBuffer

---

### 1.5.4 前端 SSE 事件处理 ✅

**文件**: `frontend/src/api/chat.ts`

- [x] 处理 `reasoning` 事件（在 InputBox.vue 中实现）
- [x] 处理 `content` 事件
- [x] 正确更新 store 状态

---

### 1.5.5 MessageList 思维链显示 ✅

**文件**: `frontend/src/components/MessageList.vue`

- [x] 为助手消息添加思维链区域
- [x] 思维链样式：灰色（#6a737d）、较小字体（0.9em）
- [x] 思维链区域可折叠（默认展开）
- [x] 最终答案使用现有 MarkdownRenderer 样式
- [x] 添加"💭 思考过程"标签

**样式要求**:
```css
.reasoning-content {
  color: #6a737d;
  font-size: 0.9em;
  border-left: 3px solid #d0d7de;
  padding-left: 1em;
  margin-bottom: 1em;
}
```

**测试**:
- [x] 更新 `MessageList.spec.ts`
- [x] 测试思维链内容渲染
- [x] 测试思维链和内容分离
- [x] 测试展开/折叠功能
- [x] 运行测试确保通过 (16 tests passed)
- [x] 验证覆盖率 ≥ 80% (97.75%)

---

### 1.5.6 Phase 1.5 验收

- [x] 所有单元测试通过 (16 tests)
- [x] 测试覆盖率 ≥ 80% (97.75%)
- [ ] 手动测试（需要用户验证）：
  - [ ] 使用支持思维链的模型（如 GLM-4.5）
  - [ ] 发送问题，验证：
    - [ ] 思考过程显示为灰色小字
    - [ ] 最终答案正常显示
    - [ ] 思维链区域可折叠
  - [ ] 多轮对话验证历史 reasoning 保留

---

## Phase 2: 流式工具调用

### 2.1 后端流式处理改造 ✅

**文件**: `backend/app/providers/zhipuai.py`

- [x] 修改 `chat_stream()` 返回类型为 `AsyncIterator[dict]`
- [x] 检测流式响应中的 `tool_calls` 字段
- [x] 累积 tool_calls 数据（流式模式逐步构建）
- [x] 返回 `{"event": "tool_call", "tool_calls": [...]}`

**验证**:
```bash
# 检查返回的流包含 tool_call 事件
```

---

### 2.2 Agent 流式工具执行 ✅

**文件**: `backend/app/agent/base.py`

- [x] 修改 `process_message_stream()` 支持工具调用
- [x] 实现"检测 tool_call → 执行工具 → 返回结果"循环
- [x] 添加工具错误处理
- [x] 更新消息历史（添加工具结果）
- [x] 支持多轮工具调用（迭代循环）

---

### 2.3 SSE 事件处理 ✅

**文件**: `backend/app/api/chat.py`

- [x] 确保 SSE 事件格式正确：
  - `event: tool_call`
  - `event: tool_result`
  - `event: tool_error`
- [x] 更新 `/api/chat/stream` 端点

---

### 2.4 前端类型定义 ✅

**文件**: `frontend/src/api/types.ts`

- [x] 扩展 `SSEEvent` 类型：
  ```typescript
  type: 'token' | 'reasoning' | 'tool_call' | 'tool_result' | 'tool_error' | 'done' | 'error'
  ```
- [x] 添加 `ToolCall` 接口
- [x] 更新相关类型

---

### 2.5 前端状态管理 ✅

**文件**: `frontend/src/stores/chat.ts`

- [x] 添加 `currentToolCalls: ToolCall[]`
- [x] 添加 `isProcessingTool: boolean`
- [x] 添加 `addToolCall()` action
- [x] 添加 `updateToolCall()` action
- [x] 添加 `clearToolCalls()` action

---

### 2.6 SSE 事件处理扩展 ✅

**文件**: `frontend/src/components/InputBox.vue`

- [x] 处理 `tool_call` 事件
- [x] 处理 `tool_result` 事件
- [x] 处理 `tool_error` 事件
- [x] 更新 store 状态

---

### 2.7 创建 ToolCard 组件 ✅

**文件**: `frontend/src/components/ToolCard.vue`

- [x] 创建组件，接收 props：
  - `toolCall: ToolCall`
- [x] 实现三种状态的 UI：
  - `executing`: 蓝色边框 + 加载动画
  - `success`: 绿色边框 + ✓
  - `error`: 红色边框 + ⚠️
- [x] 集成 `MarkdownRenderer` 显示结果
- [x] 添加 scoped 样式

---

### 2.8 MessageList 集成 ToolCard ✅

**文件**: `frontend/src/components/MessageList.vue`

- [x] 导入 `ToolCard` 组件
- [x] 显示 `currentToolCalls` 列表
- [x] 添加工具调用容器样式

**文件**: `frontend/src/components/InputBox.vue`

- [x] 在工具执行期间禁用输入框
- [x] 更新 `disabled` 属性包含 `isProcessingTool`

---

### 2.9 Phase 2 验收

- [ ] 所有单元测试通过
- [ ] 测试覆盖率 ≥ 80%
- [ ] 手动测试（需要用户验证）：
  - [ ] 发送"计算 18+25"，验证：
    - [ ] 显示"🔢 计算器 执行中..."卡片（蓝色）
    - [ ] 结果显示绿色卡片 + "✓ 完成"
    - [ ] 输入框在执行期间禁用
  - [ ] 发送"查询北京天气"，验证：
    - [ ] 工具调用流程正确
  - [ ] 发送无效工具调用（如"计算 abc"），验证：
    - [ ] 显示红色错误卡片
  - [ ] 多个工具调用串行执行

---

## 部署

### 发布检查清单

- [ ] 所有测试通过
- [ ] 代码审查完成
- [ ] 文档更新（README.md）
- [ ] 无 console.log 或调试代码
- [ ] 无 TypeScript 错误
- [ ] 无 ESLint 警告
- [ ] 性能测试通过

---

## 后续优化

### 未来增强

- [ ] 代码块默认折叠，点击展开
- [ ] 多工具并行执行
- [ ] 工具调用历史记录
- [ ] 代码块执行预览
