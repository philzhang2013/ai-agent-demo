import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ChatMessage, ToolCall } from '@/api/types'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const isLoading = ref(false)
  const sessionId = ref<string | null>(null)
  const reasoningBuffer = ref<string>('')  // 思维链缓冲区
  const currentToolCalls = ref<ToolCall[]>([])  // 当前正在执行的工具调用
  const isProcessingTool = ref(false)  // 是否正在处理工具

  function addMessage(message: ChatMessage) {
    messages.value.push(message)
  }

  function updateLastAssistantMessage(content: string) {
    const lastMessage = messages.value[messages.value.length - 1]
    if (lastMessage && lastMessage.role === 'assistant') {
      // 确保响应式更新 - 创建新对象
      messages.value[messages.value.length - 1] = {
        ...lastMessage,
        content
      }
    } else {
      addMessage({
        id: Date.now().toString(),
        role: 'assistant',
        content,
        timestamp: new Date()
      })
    }
  }

  function updateLastAssistantReasoning(reasoningContent: string) {
    const lastMessage = messages.value[messages.value.length - 1]
    if (lastMessage && lastMessage.role === 'assistant') {
      // 确保响应式更新 - 创建新对象
      messages.value[messages.value.length - 1] = {
        ...lastMessage,
        reasoningContent
      }
    } else {
      addMessage({
        id: Date.now().toString(),
        role: 'assistant',
        content: '',
        reasoningContent,
        timestamp: new Date()
      })
    }
  }

  function addAssistantMessage(content: string) {
    addMessage({
      id: Date.now().toString(),
      role: 'assistant',
      content,
      timestamp: new Date()
    })
  }

  function addUserMessage(content: string) {
    addMessage({
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date()
    })
  }

  function setLoading(loading: boolean) {
    isLoading.value = loading
    if (loading) {
      // 开始新的请求时清空思维链缓冲区和工具调用
      reasoningBuffer.value = ''
      currentToolCalls.value = []
    }
  }

  function setSessionId(id: string) {
    sessionId.value = id
  }

  function clearMessages() {
    messages.value = []
    sessionId.value = null
    reasoningBuffer.value = ''
    currentToolCalls.value = []
    isProcessingTool.value = false
  }

  function removeLastMessage() {
    messages.value.pop()
  }

  function appendToReasoningBuffer(content: string) {
    reasoningBuffer.value += content
  }

  // 工具调用相关方法
  function addToolCall(toolCall: ToolCall) {
    currentToolCalls.value.push(toolCall)
    isProcessingTool.value = true
  }

  function updateToolCall(toolId: string, updates: Partial<ToolCall>) {
    const index = currentToolCalls.value.findIndex(tc => tc.id === toolId)
    if (index !== -1) {
      currentToolCalls.value[index] = { ...currentToolCalls.value[index], ...updates }
    }
  }

  function clearToolCalls() {
    currentToolCalls.value = []
    isProcessingTool.value = false
  }

  return {
    messages,
    isLoading,
    sessionId,
    reasoningBuffer,
    currentToolCalls,
    isProcessingTool,
    addMessage,
    updateLastAssistantMessage,
    updateLastAssistantReasoning,
    addAssistantMessage,
    addUserMessage,
    setLoading,
    setSessionId,
    clearMessages,
    removeLastMessage,
    appendToReasoningBuffer,
    addToolCall,
    updateToolCall,
    clearToolCalls
  }
})
