/**
 * 会话状态管理
 * 管理会话列表、当前会话、会话切换等
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Session } from '@/api/sessions'
import { sessionsAPI } from '@/api/sessions'
import { useChatStore } from './chat'

export const useSessionStore = defineStore('session', () => {
  // 状态
  const sessions = ref<Session[]>([])
  const currentSessionId = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 请求 ID（用于处理并发切换）
  let currentRequestId = 0

  /**
   * 获取当前会话
   */
  const getCurrentSession = computed(() => {
    return sessions.value.find(s => s.id === currentSessionId.value) || null
  })

  /**
   * 加载会话列表
   */
  async function loadSessions() {
    isLoading.value = true
    error.value = null

    try {
      sessions.value = await sessionsAPI.getSessions()
    } catch (e) {
      error.value = e instanceof Error ? e.message : '加载会话列表失败'
      console.error('加载会话列表失败:', e)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 切换会话
   */
  async function switchSession(sessionId: string) {
    const requestId = ++currentRequestId
    isLoading.value = true
    error.value = null

    try {
      // 获取会话详情（含消息）
      const sessionDetail = await sessionsAPI.getSession(sessionId)

      // 只处理最新的请求响应
      if (requestId !== currentRequestId) {
        return
      }

      // 更新当前会话 ID
      currentSessionId.value = sessionId

      // 更新会话列表中的数据
      const index = sessions.value.findIndex(s => s.id === sessionId)
      if (index !== -1) {
        sessions.value[index] = {
          ...sessions.value[index],
          title: sessionDetail.title,
          updated_at: sessionDetail.updated_at
        }
      }

      // 清空并加载消息到 chatStore
      const chatStore = useChatStore()
      chatStore.clearMessages()
      chatStore.setSessionId(sessionId)

      // 添加会话的历史消息
      sessionDetail.messages.forEach(msg => {
        if (msg.role === 'user') {
          chatStore.addUserMessage(msg.content)
        } else {
          chatStore.addAssistantMessage(msg.content)
        }
      })
    } catch (e) {
      // 只处理最新的请求错误
      if (requestId === currentRequestId) {
        error.value = e instanceof Error ? e.message : '切换会话失败'
        console.error('切换会话失败:', e)
      }
    } finally {
      // 只处理最新的请求完成
      if (requestId === currentRequestId) {
        isLoading.value = false
      }
    }
  }

  /**
   * 创建新会话
   */
  async function createSession() {
    isLoading.value = true
    error.value = null

    try {
      const newSession = await sessionsAPI.createSession()

      // 添加到会话列表
      sessions.value.unshift(newSession)

      // 切换到新会话
      await switchSession(newSession.id)

      return newSession
    } catch (e) {
      error.value = e instanceof Error ? e.message : '创建会话失败'
      console.error('创建会话失败:', e)
      throw e
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 更新会话标题
   */
  async function updateSessionTitle(sessionId: string, title: string) {
    error.value = null

    try {
      const updatedSession = await sessionsAPI.updateSessionTitle(sessionId, title)

      // 更新会话列表中的数据
      const index = sessions.value.findIndex(s => s.id === sessionId)
      if (index !== -1) {
        sessions.value[index] = updatedSession
      }

      return updatedSession
    } catch (e) {
      error.value = e instanceof Error ? e.message : '更新会话标题失败'
      console.error('更新会话标题失败:', e)
      throw e
    }
  }

  /**
   * 删除会话
   */
  async function deleteSession(sessionId: string) {
    isLoading.value = true
    error.value = null

    try {
      await sessionsAPI.deleteSession(sessionId)

      // 从会话列表中移除
      const index = sessions.value.findIndex(s => s.id === sessionId)
      if (index !== -1) {
        sessions.value.splice(index, 1)
      }

      // 如果删除的是当前会话，清空当前会话
      if (currentSessionId.value === sessionId) {
        currentSessionId.value = null
        const chatStore = useChatStore()
        chatStore.clearMessages()
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : '删除会话失败'
      console.error('删除会话失败:', e)
      throw e
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 初始化：加载会话列表
   */
  async function initialize() {
    await loadSessions()

    // 如果有会话且没有当前会话，自动切换到第一个
    if (sessions.value.length > 0 && !currentSessionId.value) {
      await switchSession(sessions.value[0].id)
    }
  }

  return {
    // 状态
    sessions,
    currentSessionId,
    isLoading,
    error,

    // 计算属性
    getCurrentSession,

    // 方法
    loadSessions,
    switchSession,
    createSession,
    updateSessionTitle,
    deleteSession,
    initialize
  }
})
