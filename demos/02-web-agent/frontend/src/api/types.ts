// 聊天相关的类型定义

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  reasoningContent?: string  // 思维链内容（可选）
  timestamp: Date
}

// 工具调用接口
export interface ToolCall {
  id: string
  tool: string
  args: Record<string, any>
  status: 'executing' | 'success' | 'error'
  result?: string
  error?: string
}

export interface SSEEvent {
  type: 'token' | 'reasoning' | 'tool_call' | 'tool_result' | 'tool_error' | 'done' | 'error'
  content?: string
  tool?: string
  args?: Record<string, any>
  tool_calls?: Array<{
    id: string
    type: string
    function: {
      name: string
      arguments: string
    }
  }>
  result?: string
  session_id?: string
  error?: string
}
