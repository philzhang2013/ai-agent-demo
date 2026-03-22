import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ChatMessage } from '@/api/types'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const isLoading = ref(false)
  const sessionId = ref<string | null>(null)

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
  }

  function setSessionId(id: string) {
    sessionId.value = id
  }

  function clearMessages() {
    messages.value = []
    sessionId.value = null
  }

  function removeLastMessage() {
    messages.value.pop()
  }

  return {
    messages,
    isLoading,
    sessionId,
    addMessage,
    updateLastAssistantMessage,
    addAssistantMessage,
    addUserMessage,
    setLoading,
    setSessionId,
    clearMessages,
    removeLastMessage
  }
})
