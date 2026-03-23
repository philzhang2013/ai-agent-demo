<template>
  <div :class="['tool-card', `tool-card-${toolCall.status}`]">
    <div class="tool-header">
      <div class="tool-info">
        <span class="tool-icon">{{ getToolIcon(toolCall.tool) }}</span>
        <span class="tool-name">{{ getToolDisplayName(toolCall.tool) }}</span>
      </div>
      <div class="tool-status">
        <span v-if="toolCall.status === 'executing'" class="status-executing">
          <span class="spinner"></span>
          执行中...
        </span>
        <span v-else-if="toolCall.status === 'success'" class="status-success">✓ 完成</span>
        <span v-else-if="toolCall.status === 'error'" class="status-error">⚠️ 错误</span>
      </div>
    </div>

    <!-- 工具参数 -->
    <div v-if="toolCall.status === 'executing'" class="tool-args">
      <span class="args-label">参数:</span>
      <code class="args-content">{{ formatArgs(toolCall.args) }}</code>
    </div>

    <!-- 工具结果 -->
    <div v-if="toolCall.result" class="tool-result">
      <div class="result-label">结果:</div>
      <MarkdownRenderer :content="toolCall.result" />
    </div>

    <!-- 工具错误 -->
    <div v-if="toolCall.error" class="tool-error">
      <span class="error-icon">⚠️</span>
      <span class="error-message">{{ toolCall.error }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ToolCall } from '@/api/types'
import MarkdownRenderer from './MarkdownRenderer.vue'

const props = defineProps<{
  toolCall: ToolCall
}>()

function getToolIcon(toolName: string): string {
  const icons: Record<string, string> = {
    'calculator': '🔢',
    'get_weather': '🌤️'
  }
  return icons[toolName] || '🔧'
}

function getToolDisplayName(toolName: string): string {
  const names: Record<string, string> = {
    'calculator': '计算器',
    'get_weather': '天气查询'
  }
  return names[toolName] || toolName
}

function formatArgs(args: Record<string, any>): string {
  return JSON.stringify(args, null, 2)
}
</script>

<style scoped>
.tool-card {
  margin: 12px 0;
  border-radius: 8px;
  border: 2px solid;
  overflow: hidden;
  background: white;
  transition: all 0.3s;
}

.tool-card-executing {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
}

.tool-card-success {
  border-color: #10b981;
  background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
}

.tool-card-error {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2 0%, #ffffff 100%);
}

.tool-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.tool-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tool-icon {
  font-size: 20px;
}

.tool-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 14px;
}

.tool-status {
  font-size: 13px;
  font-weight: 500;
}

.status-executing {
  color: #3b82f6;
  display: flex;
  align-items: center;
  gap: 6px;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid #3b82f6;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.status-success {
  color: #10b981;
}

.status-error {
  color: #ef4444;
}

.tool-args {
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.03);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.args-label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
  display: block;
  margin-bottom: 6px;
}

.args-content {
  display: block;
  padding: 8px 12px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
  font-size: 12px;
  color: #374151;
  overflow-x: auto;
}

.tool-result {
  padding: 12px 16px;
}

.result-label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
  margin-bottom: 8px;
}

.tool-error {
  padding: 12px 16px;
  background: #fef2f2;
  border-top: 1px solid #fecaca;
  display: flex;
  align-items: center;
  gap: 8px;
}

.error-icon {
  font-size: 18px;
}

.error-message {
  color: #dc2626;
  font-size: 13px;
  flex: 1;
}
</style>
