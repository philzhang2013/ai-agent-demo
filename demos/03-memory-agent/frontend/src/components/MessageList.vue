<template>
  <div class="message-list">
    <!-- 空状态 -->
    <div v-if="messages.length === 0 && !isLoading" class="empty-state">
      <div class="empty-icon">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h3>开始新对话</h3>
      <p>向 AI 智能助手提问任何问题</p>
    </div>

    <!-- 消息列表 -->
    <div
      v-for="message in messages"
      :key="message.id"
      :class="['message-wrapper', `message-wrapper-${message.role}`]"
    >
      <div :class="['message', `message-${message.role}`]">
        <div class="message-avatar">
          <svg v-if="message.role === 'assistant'" width="20" height="20" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" fill="currentColor" fill-opacity="0.1"/>
            <path d="M12 8V12L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="8" r="4" fill="currentColor"/>
            <path d="M4 20C4 16.6863 6.68629 14 10 14H14C17.3137 14 20 16.6863 20 20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="message-content">
          <!-- 助手消息：显示思维链（如果有） -->
          <div v-if="message.role === 'assistant' && message.reasoningContent" class="reasoning-section">
            <div class="reasoning-header" @click="toggleReasoning(message.id)">
              <span class="reasoning-label">💭 思考过程</span>
              <span class="reasoning-toggle">{{ isReasoningExpanded(message.id) ? '▼' : '▶' }}</span>
            </div>
            <div v-show="isReasoningExpanded(message.id)" class="reasoning-content">
              <MarkdownRenderer :content="message.reasoningContent" />
            </div>
          </div>

          <!-- 加载状态或有内容时显示 -->
          <div v-if="message.content || message.role === 'user'" class="message-text">
            <!-- 助手消息使用 Markdown 渲染，用户消息使用纯文本 -->
            <MarkdownRenderer v-if="message.role === 'assistant'" :content="message.content" />
            <span v-else>{{ message.content }}</span>
          </div>
          <!-- 空的助手消息显示加载动画 -->
          <div v-else class="message-text loading">
            <span class="loading-dots"></span>
          </div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>
    </div>

    <!-- 工具调用卡片（显示在最后一条助手消息之后） -->
    <div v-if="currentToolCalls.length > 0" class="tool-calls-container">
      <ToolCard
        v-for="toolCall in currentToolCalls"
        :key="toolCall.id"
        :tool-call="toolCall"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useChatStore } from '@/stores/chat'
import MarkdownRenderer from './MarkdownRenderer.vue'
import ToolCard from './ToolCard.vue'

const chatStore = useChatStore()

const messages = computed(() => chatStore.messages)
const isLoading = computed(() => chatStore.isLoading)
const currentToolCalls = computed(() => chatStore.currentToolCalls)

// 思维链展开/折叠状态管理（true = 折叠，false = 展开，默认展开）
const collapsedReasonings = ref<Record<string, boolean>>({})

function toggleReasoning(messageId: string) {
  collapsedReasonings.value[messageId] = !collapsedReasonings.value[messageId]
}

function isReasoningExpanded(messageId: string): boolean {
  // 默认展开（undefined 或 false 都表示展开）
  return !collapsedReasonings.value[messageId]
}

function formatTime(date: Date): string {
  const now = new Date()
  const diff = now.getTime() - new Date(date).getTime()
  const seconds = Math.floor(diff / 1000)

  if (seconds < 60) return '刚刚'
  if (seconds < 3600) return `${Math.floor(seconds / 60)} 分钟前`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} 小时前`

  return new Date(date).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.message-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
  color: #9ca3af;
}

.empty-icon {
  margin-bottom: 16px;
  color: #d1d5db;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: #6b7280;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
  color: #9ca3af;
}

.message-wrapper {
  display: flex;
  animation: messageSlide 0.3s ease-out;
}

@keyframes messageSlide {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-wrapper-user {
  justify-content: flex-end;
}

.message-wrapper-assistant {
  justify-content: flex-start;
}

.message {
  display: flex;
  gap: 12px;
  max-width: 80%;
}

.message-user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.message-assistant .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message-user .message-avatar {
  background: #f3f4f6;
  color: #6b7280;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  word-break: break-word;
  font-size: 15px;
}

.message-assistant .message-text {
  background: #f3f4f6;
  color: #1f2937;
  border-top-left-radius: 4px;
}

.message-user .message-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-top-right-radius: 4px;
}

.message-time {
  font-size: 12px;
  color: #9ca3af;
  padding: 0 4px;
}

.message-user .message-time {
  text-align: right;
}

.loading {
  display: flex;
  align-items: center;
  min-width: 60px;
}

.loading-dots {
  display: inline-flex;
  gap: 4px;
}

.loading-dots::before,
.loading-dots::after {
  content: '';
  width: 8px;
  height: 8px;
  background: #6b7280;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots::before {
  animation-delay: -0.32s;
}

.loading-dots::after {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 思维链样式 */
.reasoning-section {
  margin-bottom: 8px;
}

.reasoning-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 12px;
  background: #f9fafb;
  border-radius: 8px;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;
}

.reasoning-header:hover {
  background: #f3f4f6;
}

.reasoning-label {
  font-size: 12px;
  color: #6a737d;
  font-weight: 500;
}

.reasoning-toggle {
  font-size: 10px;
  color: #6a737d;
  transition: transform 0.2s;
}

.reasoning-content {
  padding: 8px 12px;
  margin-top: 4px;
  background: #fafbfc;
  border-left: 3px solid #d0d7de;
  border-radius: 4px;
  color: #6a737d;
  font-size: 0.9em;
  line-height: 1.5;
}

.reasoning-content :deep(.markdown-renderer) {
  color: #6a737d;
  font-size: 0.9em;
}

/* 工具调用容器 */
.tool-calls-container {
  padding: 0 24px;
  animation: toolCallsSlide 0.3s ease-out;
}

@keyframes toolCallsSlide {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
