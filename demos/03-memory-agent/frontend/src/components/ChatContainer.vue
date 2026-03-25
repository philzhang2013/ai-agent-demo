<template>
  <div class="chat-container">
    <!-- 顶部工具栏 -->
    <div class="chat-header">
      <div class="header-left">
        <div v-if="isEditingTitle" class="title-edit">
          <el-input
            v-model="editingTitle"
            size="small"
            :maxlength="200"
            @blur="handleSaveTitle"
            @keyup.enter="handleSaveTitle"
            @keyup.esc="cancelEditTitle"
            ref="titleInputRef"
          />
        </div>
        <h2 v-else class="session-title" @click="startEditTitle">
          {{ currentTitle }}
        </h2>
        <span class="status">在线</span>
      </div>
      <div class="header-right">
        <el-button
          type="info"
          :icon="Edit"
          circle
          size="small"
          @click="startEditTitle"
          title="编辑标题"
          :disabled="isEditingTitle"
        />
        <el-button
          type="danger"
          :icon="Delete"
          circle
          size="small"
          @click="handleClear"
          title="清空对话"
        />
      </div>
    </div>

    <!-- 消息区域 -->
    <div class="chat-messages" ref="messagesContainer">
      <MessageList />
    </div>

    <!-- 输入区域 -->
    <div class="chat-input">
      <InputBox />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch, computed } from 'vue'
import { Delete, Edit } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import MessageList from './MessageList.vue'
import InputBox from './InputBox.vue'
import { useChatStore } from '@/stores/chat'
import { useSessionStore } from '@/stores/sessionStore'

const chatStore = useChatStore()
const sessionStore = useSessionStore()
const messagesContainer = ref<HTMLElement>()
const titleInputRef = ref<HTMLInputElement>()
const isEditingTitle = ref(false)
const editingTitle = ref('')

/**
 * 当前会话标题
 */
const currentTitle = computed(() => {
  const currentSession = sessionStore.getCurrentSession
  return currentSession?.title || 'AI 智能助手'
})

/**
 * 开始编辑标题
 */
async function startEditTitle() {
  if (!sessionStore.currentSessionId) {
    ElMessage.warning('请先选择或创建一个会话')
    return
  }

  const currentSession = sessionStore.getCurrentSession
  if (!currentSession) {
    return
  }

  editingTitle.value = currentSession.title
  isEditingTitle.value = true

  await nextTick()
  titleInputRef.value?.focus()
  titleInputRef.value?.select()
}

/**
 * 保存标题
 */
async function handleSaveTitle() {
  if (!editingTitle.value.trim()) {
    ElMessage.warning('标题不能为空')
    return
  }

  if (!sessionStore.currentSessionId) {
    return
  }

  try {
    await sessionStore.updateSessionTitle(sessionStore.currentSessionId, editingTitle.value.trim())
    ElMessage.success('标题已更新')
  } catch (error) {
    console.error('更新标题失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '更新标题失败')
  } finally {
    isEditingTitle.value = false
  }
}

/**
 * 取消编辑标题
 */
function cancelEditTitle() {
  isEditingTitle.value = false
  editingTitle.value = ''
}

// 当有新消息时，滚动到底部
watch(() => chatStore.messages.length, async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
})

function handleClear() {
  chatStore.clearMessages()
}
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 140px);
  max-height: 800px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.session-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.session-title:hover {
  background: rgba(0, 0, 0, 0.05);
}

.title-edit {
  display: flex;
  align-items: center;
}

.title-edit .el-input {
  width: 200px;
}

.status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: #d1fae5;
  color: #065f46;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status::before {
  content: '';
  width: 6px;
  height: 6px;
  background: #10b981;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.header-right {
  display: flex;
  gap: 8px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 24px;
  scroll-behavior: smooth;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

.chat-input {
  padding: 16px 24px;
  background: #ffffff;
  border-top: 1px solid #e5e7eb;
}
</style>
