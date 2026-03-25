<template>
  <div
    class="session-item"
    :class="{ active: isActive }"
    @click="$emit('select', session.id)"
  >
    <div class="session-content">
      <div class="session-title">{{ session.title || '新对话' }}</div>
      <div v-if="session.last_message" class="session-preview">
        {{ session.last_message }}
      </div>
      <div class="session-meta">
        <span class="session-time">{{ formattedTime }}</span>
        <span v-if="session.message_count !== undefined" class="session-count">
          {{ session.message_count }} 条消息
        </span>
      </div>
    </div>
    <button
      v-if="showDelete"
      class="delete-btn"
      @click.stop="$emit('delete', session.id)"
      title="删除会话"
    >
      ×
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Session } from '@/api/sessions'

interface Props {
  session: Session
  isActive?: boolean
  showDelete?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isActive: false,
  showDelete: false
})

interface Emits {
  (e: 'select', id: string): void
  (e: 'delete', id: string): void
}

defineEmits<Emits>()

/**
 * 格式化时间
 */
const formattedTime = computed(() => {
  const date = new Date(props.session.updated_at)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) {
    return '刚刚'
  } else if (diffMins < 60) {
    return `${diffMins} 分钟前`
  } else if (diffHours < 24) {
    return `${diffHours} 小时前`
  } else if (diffDays < 7) {
    return `${diffDays} 天前`
  } else {
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  }
})
</script>

<style scoped>
.session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  cursor: pointer;
  border-radius: 8px;
  transition: background-color 0.2s, border-color 0.2s;
  border: 2px solid transparent;
  gap: 8px;
}

.session-item:hover {
  background-color: var(--el-bg-color-page);
}

.session-item.active {
  background-color: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary);
  font-weight: 500;
}

.session-content {
  flex: 1;
  min-width: 0;
}

.session-title {
  font-size: 14px;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-preview {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 4px;
}

.session-meta {
  display: flex;
  gap: 8px;
  font-size: 11px;
  color: var(--el-text-color-placeholder);
}

.session-time,
.session-count {
  white-space: nowrap;
}

.delete-btn {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: var(--el-text-color-placeholder);
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  border-radius: 4px;
  opacity: 0;
  transition: all 0.2s;
}

.session-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background-color: var(--el-color-danger-light-9);
  color: var(--el-color-danger);
}

/* 移动端优化 */
@media (max-width: 767px) {
  .delete-btn {
    opacity: 1;
  }
}
</style>
