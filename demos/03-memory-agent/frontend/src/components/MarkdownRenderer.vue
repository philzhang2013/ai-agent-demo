<template>
  <div class="markdown-renderer" v-html="sanitizedHtml"></div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

// Props
interface Props {
  content: string
}

const props = defineProps<Props>()

// 复制状态
const copiedCodeIndex = ref<Set<number>>(new Set())

// 监听内容变化，重置复制状态
watch(() => props.content, () => {
  copiedCodeIndex.value.clear()
})

/**
 * 配置 marked 选项
 */
marked.setOptions({
  highlight: (code: string, language: string) => {
    if (language && hljs.getLanguage(language)) {
      try {
        return hljs.highlight(code, { language }).value
      } catch (e) {
        console.error('Highlight.js error:', e)
      }
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true,
})

/**
 * DOMPurify 配置 - XSS 防护
 */
const purifyConfig = {
  ALLOWED_TAGS: [
    'p', 'br', 'strong', 'em', 'code', 'pre', 'blockquote',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'a', 'table', 'thead', 'tbody', 'tr', 'td', 'th',
    'div', 'span', 'hr', 'img', 'button',
  ],
  ALLOWED_ATTR: [
    'href', 'class', 'id', 'style', 'data-*',
    'src', 'alt', 'title', 'width', 'height',
  ],
  ALLOW_DATA_ATTR: true,
}

/**
 * 为代码块添加行号
 */
const addLineNumbers = (html: string): string => {
  // marked.js 输出格式: <pre><code class="language-js">...</code></pre>
  // 使用更灵活的 regex 匹配
  return html.replace(/<pre><code\s+class="language-(\w+)"[^>]*>([\s\S]*?)<\/code><\/pre>/g, (match, lang, code) => {
    // 不进行 HTML 实体解码，直接使用 marked 已经转义的内容
    const lines = code.trim().split('\n')
    const lineNumbersHtml = lines.map((_, i) => `<span class="line-number">${i + 1}</span>`).join('')
    // 保持原始转义状态，只需要包装在 code-line span 中
    const codeHtml = lines.map(line => `<span class="code-line">${line}</span>`).join('\n')

    return `
      <div class="code-block-wrapper" data-language="${lang}">
        <div class="code-header">
          <span class="code-language">${lang}</span>
          <button class="copy-button" data-code-index="${Math.random()}">复制</button>
        </div>
        <div class="code-content">
          <div class="line-numbers">${lineNumbersHtml}</div>
          <pre><code class="language-${lang}">${codeHtml}</code></pre>
        </div>
      </div>
    `
  })
}

/**
 * 处理复制的代码内容（去除行号）
 */
const copyCode = (button: HTMLButtonElement) => {
  const wrapper = button.closest('.code-block-wrapper')
  if (!wrapper) return

  const codeElement = wrapper.querySelector('pre code')
  if (!codeElement) return

  // 获取纯代码内容（去除行号 span）
  const codeLines = codeElement.querySelectorAll('.code-line')
  const code = Array.from(codeLines).map(line => line.textContent).join('\n')

  // 复制到剪贴板
  navigator.clipboard.writeText(code).then(() => {
    const originalText = button.textContent
    button.textContent = '已复制!'
    button.classList.add('copied')

    setTimeout(() => {
      button.textContent = originalText
      button.classList.remove('copied')
    }, 2000)
  }).catch(err => {
    console.error('复制失败:', err)
  })
}

/**
 * 解析 Markdown 并清理 HTML
 */
const sanitizedHtml = computed(() => {
  // 1. 解析 Markdown
  let html = marked.parse(props.content) as string

  // 2. 为代码块添加行号
  html = addLineNumbers(html)

  // 3. 清理 XSS
  html = DOMPurify.sanitize(html, purifyConfig)

  return html
})

/**
 * 组件挂载后绑定复制按钮事件
 */
import { onMounted, onUnmounted } from 'vue'

onMounted(() => {
  // 使用事件委托处理复制按钮点击
  document.addEventListener('click', handleCopyClick as EventListener)
})

onUnmounted(() => {
  document.removeEventListener('click', handleCopyClick as EventListener)
})

const handleCopyClick = (e: Event) => {
  const target = e.target as HTMLElement
  if (target.classList.contains('copy-button')) {
    e.preventDefault()
    copyCode(target as HTMLButtonElement)
  }
}
</script>

<style scoped>
.markdown-renderer {
  line-height: 1.6;
  color: #333;
}

.markdown-renderer :deep(h1),
.markdown-renderer :deep(h2),
.markdown-renderer :deep(h3),
.markdown-renderer :deep(h4),
.markdown-renderer :deep(h5),
.markdown-renderer :deep(h6) {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-weight: 600;
}

.markdown-renderer :deep(h1) {
  font-size: 2em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-renderer :deep(h2) {
  font-size: 1.5em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-renderer :deep(p) {
  margin: 0.5em 0;
}

.markdown-renderer :deep(ul),
.markdown-renderer :deep(ol) {
  padding-left: 2em;
}

.markdown-renderer :deep(li) {
  margin: 0.25em 0;
}

.markdown-renderer :deep(blockquote) {
  border-left: 4px solid #dfe2e5;
  padding-left: 1em;
  margin: 1em 0;
  color: #6a737d;
  background-color: #f6f8fa;
  padding: 0.5em 1em;
  border-radius: 4px;
}

.markdown-renderer :deep(code:not(pre code)) {
  background-color: #f6f8fa;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
  font-size: 0.9em;
}

.markdown-renderer :deep(pre code) {
  background-color: transparent;
  padding: 0;
}

.markdown-renderer :deep(a) {
  color: #0969da;
  text-decoration: none;
}

.markdown-renderer :deep(a:hover) {
  text-decoration: underline;
}

/* 代码块样式 */
.markdown-renderer :deep(.code-block-wrapper) {
  margin: 1em 0;
  border: 1px solid #d0d7de;
  border-radius: 6px;
  overflow: hidden;
  background-color: #f6f8fa;
}

.markdown-renderer :deep(.code-header) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5em 1em;
  background-color: #d8dee4;
  border-bottom: 1px solid #d0d7de;
  font-size: 0.85em;
}

.markdown-renderer :deep(.code-language) {
  color: #24292f;
  font-weight: 500;
}

.markdown-renderer :deep(.copy-button) {
  background-color: #f6f8fa;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  padding: 0.2em 0.6em;
  font-size: 0.8em;
  cursor: pointer;
  transition: all 0.2s;
}

.markdown-renderer :deep(.copy-button:hover) {
  background-color: #ffffff;
  border-color: #0969da;
}

.markdown-renderer :deep(.copy-button.copied) {
  background-color: #1a7f37;
  color: white;
  border-color: #1a7f37;
}

.markdown-renderer :deep(.code-content) {
  display: flex;
  overflow-x: auto;
}

.markdown-renderer :deep(.line-numbers) {
  padding: 1em 0.5em;
  background-color: #f6f8fa;
  border-right: 1px solid #d0d7de;
  text-align: right;
  user-select: none;
  color: #6e7781;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
  font-size: 0.9em;
  line-height: 1.5;
  min-width: 3em;
}

.markdown-renderer :deep(.line-number) {
  display: block;
}

.markdown-renderer :deep(.code-line) {
  display: block;
  min-height: 1.5em;
}

.markdown-renderer :deep(pre) {
  margin: 0;
  padding: 1em;
  background-color: transparent;
  overflow-x: auto;
}

.markdown-renderer :deep(pre code) {
  font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
  font-size: 0.9em;
  line-height: 1.5;
  background-color: transparent;
}

.markdown-renderer :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}

.markdown-renderer :deep(th),
.markdown-renderer :deep(td) {
  border: 1px solid #d0d7de;
  padding: 0.5em 1em;
  text-align: left;
}

.markdown-renderer :deep(th) {
  background-color: #f6f8fa;
  font-weight: 600;
}

.markdown-renderer :deep(hr) {
  border: none;
  border-top: 1px solid #d0d7de;
  margin: 2em 0;
}

.markdown-renderer :deep(img) {
  max-width: 100%;
  height: auto;
}
</style>
