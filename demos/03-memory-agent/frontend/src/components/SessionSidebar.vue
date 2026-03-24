<template>
  <div class="session-sidebar">
    <div class="sidebar-header">
      <h2 class="sidebar-title">会话列表</h2>
      <el-button
        type="primary"
        size="small"
        @click="handleCreateSession"
        :loading="sessionStore.isLoading"
      >
        <el-icon><Plus /></el-icon>
        新建会话
      </el-button>
    </div>

    <div class="sidebar-content">
      <!-- 加载状态 -->
      <div v-if="sessionStore.isLoading && sessionStore.sessions.length === 0" class="loading-state">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载会话列表...</span>
      </div>

      <!-- 空状态 -->
      <div v-else-if="sessionStore.sessions.length === 0" class="empty-state">
        <el-empty description="暂无会话" :image-size="80" />
        <el-button type="primary" @click="handleCreateSession">创建第一个会话</el-button>
      </div>

      <!-- 会话列表 -->
      <div v-else class="session-list">
        <SessionItem
          v-for="session in sessionStore.sessions"
          :key="session.id"
          :session="session"
          :is-active="session.id === sessionStore.currentSessionId"
          :show-delete="true"
          @select="handleSelectSession"
          @delete="handleDeleteSession"
        />
      </div>
    </div>

    <!-- 错误提示 -->
    <el-alert
      v-if="sessionStore.error"
      type="error"
      :title="sessionStore.error"
      :closable="true"
      @close="sessionStore.error = null"
      class="error-alert"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { Plus, Loading } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import SessionItem from './SessionItem.vue'
import { useSessionStore } from '@/stores/sessionStore'

const sessionStore = useSessionStore()

/**
 * 加载会话列表
 */
onMounted(async () => {
  try {
    await sessionStore.initialize()
  } catch (error) {
    console.error('初始化会话列表失败:', error)
  }
})

/**
 * 创建新会话
 */
async function handleCreateSession() {
  try {
    await sessionStore.createSession()
    ElMessage.success('已创建新会话')
  } catch (error) {
    console.error('创建会话失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '创建会话失败')
  }
}

/**
 * 选择会话
 */
async function handleSelectSession(sessionId: string) {
  // 如果已选中，不做处理
  if (sessionId === sessionStore.currentSessionId) {
    return
  }

  try {
    await sessionStore.switchSession(sessionId)
  } catch (error) {
    console.error('切换会话失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '切换会话失败')
  }
}

/**
 * 删除会话
 */
async function handleDeleteSession(sessionId: string) {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个会话吗？此操作不可恢复。',
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    await sessionStore.deleteSession(sessionId)
    ElMessage.success('会话已删除')
  } catch (error) {
    // 用户取消删除，不显示错误
    if (error === 'cancel') {
      return
    }
    console.error('删除会话失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '删除会话失败')
  }
}
</script>

<style scoped>
.session-sidebar {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color);
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color);
  gap: 8px;
}

.sidebar-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  white-space: nowrap;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 12px;
  color: var(--el-text-color-secondary);
}

.loading-state .el-icon {
  font-size: 24px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 16px;
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.error-alert {
  margin: 0 12px 12px;
  flex-shrink: 0;
}

/* 移动端优化 */
@media (max-width: 767px) {
  .session-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    width: 280px;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }

  .session-sidebar.open {
    transform: translateX(0);
  }
}
</style>
