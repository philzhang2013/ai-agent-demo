# 变更提案：Markdown 渲染 + 流式工具调用

**状态**: 提案
**创建时间**: 2026-03-23
**优先级**: 高
**预计时间**: 12-18 小时

---

## 概述

为 Demo 2 Web Agent 添加两个核心功能：

1. **Markdown 渲染**：前端支持 Markdown 格式显示（代码高亮、行号、复制按钮）
2. **流式输出支持工具调用**：在 SSE 流式输出中支持函数调用（计算器、天气查询）

---

## 问题背景

### 当前限制

1. **前端纯文本显示**
  - AI 回复只支持纯文本
  - 无法渲染代码块、列表、链接等格式
  - 代码可读性差，用户体验不佳
2. **流式模式无工具调用**
  - 当前 `process_message_stream()` 方法注释明确写着"不支持工具调用"
  - 工具调用只能在非流式模式下使用
  - 但用户界面主要使用流式接口

### 用户需求

- **Markdown 渲染**：支持代码块（带语法高亮、行号、复制按钮）
- **流式工具调用**：在流式输出中支持工具调用
- **工具调用期间禁用用户输入**：防止状态混乱

---

## 建议方案

### Phase 1: Markdown 渲染

**技术栈**：

- `marked` ^12.0.0 - Markdown 解析
- `dompurify` ^3.0.6 - XSS 清理
- `highlight.js` ^11.9.0 - 代码高亮

**涉及文件**：

- `frontend/package.json` - 添加依赖
- `frontend/src/components/MarkdownRenderer.vue` - 新建组件
- `frontend/src/components/MessageList.vue` - 集成 Markdown 渲染
- `frontend/src/components/__tests__/MarkdownRenderer.spec.ts` - 单元测试

### Phase 2: 流式工具调用

**后端改造**：

- `backend/app/providers/zhipuai.py` - 扩展流式处理，检测 tool_calls
- `backend/app/agent/base.py` - 修改 process_message_stream 支持工具调用
- `backend/app/api/chat.py` - 更新 SSE 事件类型

**前端改造**：

- `frontend/src/api/types.ts` - 扩展 SSEEvent 类型
- `frontend/src/stores/chat.ts` - 添加工具状态管理
- `frontend/src/components/ToolCard.vue` - 新建工具卡片组件
- `frontend/src/components/MessageList.vue` - 集成工具卡片展示

### 移除功能不过

- **非流式聊天接口**：`POST /api/chat`（工具调用完成后可以移除）
- **说明**：简化架构，专注于流式体验

---

## 验收标准

### Phase 1: Markdown 渲染

- 支持 `marked` 解析 Markdown
- 支持 `DOMPurify` 清理 XSS
- 支持常见语言的代码高亮
- 代码块显示行号
- 代码块有复制按钮
- 单元测试覆盖率 ≥ 80%
- 前端单元测试通过

### Phase 2: 流式工具调用

- 后端流式输出支持工具调用检测
- 工具调用期间禁用用户输入
- 工具调用中显示"执行中"状态
- 工具调用失败显示红色警告
- 工具结果用 Markdown 渲染
- 多个工具调用串行执行
- 单元测试覆盖率 ≥ 80%
- 前端单元测试通过

---

## 时间估算


| Phase       | 任务          | 预估时间    |
| ----------- | ----------- | ------- |
| **Phase 1** | Markdown 渲染 | 4-6 小时  |
| **Phase 2** | 流式工具调用      | 8-12 小时 |


**总计**: 12-18 小时

---

## 风险和未知数

### 高风险项


| 风险              | 影响  | 缓解措施                   |
| --------------- | --- | ---------------------- |
| LLM 流式响应格式变化    | 高   | 先调用 API 测试响应格式；灵活的解析逻辑 |
| 工具调用时流中断        | 中   | 心跳检测 + 重连机制            |
| Markdown XSS 攻击 | 低   | DOMPurify 清理 + 白名单策略   |


### 未知数

1. **智谱 AI 工具调用在流式中的行为** - 需要实际测试验证
2. **性能影响** - Markdown 渲染性能（长文本）、多工具串行执行的总时间
3. **状态复杂度** - 前端状态管理重构、边界情况处理

---

## 下一步

1. **创建设计文档** (design.md) - 详细的技术实现方案
2. **创建任务清单** (tasks.md) - 实施步骤分解
3. **开始实施** - 遵循 TDD 工作流

---

**变更 ID**: `markdown-and-streaming-tools`
**相关 Demo**: Demo 2 - Web Agent
**类型**: 功能增强
**复杂度**: 中-高