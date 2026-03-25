<template>
  <div class="input-box">
    <div class="input-container">
      <div class="input-wrapper">
        <textarea
          v-model="inputMessage"
          class="message-input"
          placeholder="发送消息给 AI 助手..."
          rows="1"
          @keydown="handleKeydown"
          @input="handleInput"
          :disabled="isLoading || isProcessingTool"
          ref="textareaRef"
        />
        <el-button
          type="primary"
          :icon="Promotion"
          @click="handleSend"
          :loading="isLoading"
          :disabled="!inputMessage.trim() || isLoading || isProcessingTool"
          class="send-button"
          circle
        />
      </div>
      <div class="input-footer">
        <span class="input-hint">{{ inputMessage.length }} / 2000</span>
        <span class="input-shortcut">Enter 发送，Shift + Enter 换行</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue'
import { Promotion } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useChatStore } from '@/stores/chat'
import { useSessionStore } from '@/stores/sessionStore'
import { chatAPI } from '@/api/chat'

const chatStore = useChatStore()
const sessionStore = useSessionStore()
const inputMessage = ref('')
const textareaRef = ref<HTMLTextAreaElement>()
const isStreaming = ref(false)

// 工具处理状态
const isProcessingTool = computed(() => chatStore.isProcessingTool)

// 自动调整 textarea 高度
function handleInput() {
  const textarea = textareaRef.value
  if (!textarea) return

  // 限制最大长度
  if (inputMessage.value.length > 2000) {
    inputMessage.value = inputMessage.value.slice(0, 2000)
  }

  // 自动调整高度
  textarea.style.height = 'auto'
  const newHeight = Math.min(textarea.scrollHeight, 150)
  textarea.style.height = newHeight + 'px'
}

// 处理键盘事件
function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

async function handleSend() {
  const message = inputMessage.value.trim()
  if (!message || isStreaming.value) return

  // 判断是否是第一条消息（用于自动更新标题）
  const isFirstMessage = chatStore.messages.length === 0

  // 添加用户消息
  chatStore.addUserMessage(message)
  inputMessage.value = ''

  // 重置 textarea 高度
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
  }

  // 设置加载状态
  chatStore.setLoading(true)
  isStreaming.value = true

  // 创建初始空消息用于流式显示
  chatStore.addAssistantMessage('')
  let tempContent = ''

  try {
    chatAPI.sendMessageStream(
      message,
      (event) => {
        switch (event.type) {
          case 'reasoning':
            // 收到思维链内容，更新 reasoningBuffer
            if (event.content) {
              chatStore.appendToReasoningBuffer(event.content)
              chatStore.updateLastAssistantReasoning(chatStore.reasoningBuffer)
            }
            break

          case 'token':
            // 收到普通内容，实时更新
            if (event.content) {
              tempContent += event.content
              chatStore.updateLastAssistantMessage(tempContent)
            }
            break

          case 'tool_call':
            // 收到工具调用
            if (event.tool_calls) {
              event.tool_calls.forEach(tc => {
                chatStore.addToolCall({
                  id: tc.id,
                  tool: tc.function.name,
                  args: JSON.parse(tc.function.arguments),
                  status: 'executing'
                })
              })
            }
            break

          case 'tool_result':
            // 收到工具结果
            if (event.tool && event.result !== undefined) {
              // 找到对应的工具调用并更新
              const toolCall = chatStore.currentToolCalls.find(tc => tc.tool === event.tool)
              if (toolCall) {
                chatStore.updateToolCall(toolCall.id, {
                  status: 'success',
                  result: event.result
                })
              }
            }
            break

          case 'tool_error':
            // 收到工具错误
            if (event.tool && event.error) {
              const toolCall = chatStore.currentToolCalls.find(tc => tc.tool === event.tool)
              if (toolCall) {
                chatStore.updateToolCall(toolCall.id, {
                  status: 'error',
                  error: event.error
                })
              }
            }
            break

          case 'done':
            // 完成
            isStreaming.value = false
            chatStore.clearToolCalls()
            if (event.session_id) {
              chatStore.setSessionId(event.session_id)
            }
            chatStore.setLoading(false)

            // 如果是第一条消息，更新会话标题为消息内容（截断到30个字符）
            if (isFirstMessage && sessionStore.currentSessionId) {
              const title = message.length > 30 ? message.slice(0, 30) + '...' : message
              sessionStore.updateSessionTitle(sessionStore.currentSessionId, title).catch(() => {
                // 静默处理错误，不影响用户体验
              })
            }
            break

          case 'error':
            // 错误
            isStreaming.value = false
            chatStore.clearToolCalls()
            ElMessage.error(event.error || '发送失败')
            chatStore.setLoading(false)
            // 移除空消息
            if (tempContent === '' && chatStore.reasoningBuffer === '') {
              chatStore.removeLastMessage()
            }
            break
        }
      },
      sessionStore.currentSessionId || undefined
    )
  } catch (error) {
    isStreaming.value = false
    chatStore.clearToolCalls()
    ElMessage.error('发送失败，请稍后重试')
    chatStore.setLoading(false)
  }
}
</script>

<style scoped>
.input-box {
  width: 100%;
}

.input-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  padding: 12px 16px;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 16px;
  transition: all 0.2s;
}

.input-wrapper:focus-within {
  border-color: #667eea;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.message-input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  resize: none;
  font-size: 15px;
  line-height: 1.5;
  color: #1f2937;
  font-family: inherit;
  min-height: 24px;
  max-height: 150px;
  overflow-y: auto;
}

.message-input::placeholder {
  color: #9ca3af;
}

.message-input:disabled {
  color: #9ca3af;
  cursor: not-allowed;
}

.send-button {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.send-button:not(:disabled):hover {
  transform: scale(1.05);
}

.send-button:disabled {
  background: #d1d5db;
  transform: none;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 4px;
}

.input-hint {
  font-size: 12px;
  color: #9ca3af;
}

.input-shortcut {
  font-size: 12px;
  color: #d1d5db;
}
</style>
