import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { nextTick } from 'vue'
import MessageList from '../MessageList.vue'
import { useChatStore } from '@/stores/chat'

/**
 * MessageList 组件单元测试
 *
 * 测试覆盖：
 * 1. MarkdownRenderer 集成
 * 2. 消息显示
 * 3. 加载状态
 * 4. 空状态
 */

describe('MessageList.vue', () => {
  beforeEach(() => {
    // 为每个测试创建新的 Pinia 实例
    setActivePinia(createPinia())
  })

  describe('MarkdownRenderer 集成', () => {
    it('应该为助手消息渲染 Markdown', () => {
      const chatStore = useChatStore()
      chatStore.messages = [
        {
          id: '1',
          role: 'assistant',
          content: '# 标题\n\n**粗体** 和 `代码`',
          timestamp: new Date()
        }
      ]

      const wrapper = mount(MessageList)

      // 检查 MarkdownRenderer 组件存在
      expect(wrapper.findComponent({ name: 'MarkdownRenderer' }).exists()).toBe(true)
      // 检查 Markdown 内容被渲染
      expect(wrapper.html()).toContain('<h1>')
      expect(wrapper.html()).toContain('<strong>')
    })

    it('应该为用户消息显示纯文本（不使用 Markdown）', () => {
      const chatStore = useChatStore()
      chatStore.messages = [
        {
          id: '1',
          role: 'user',
          content: '# 这是纯文本，不应该被解析为 Markdown',
          timestamp: new Date()
        }
      ]

      const wrapper = mount(MessageList)

      // 用户消息不应该有 MarkdownRenderer
      expect(wrapper.findComponent({ name: 'MarkdownRenderer' }).exists()).toBe(false)
      // 内容应该直接显示
      expect(wrapper.text()).toContain('# 这是纯文本，不应该被解析为 Markdown')
    })

    it('应该渲染代码块并显示复制按钮', () => {
      const chatStore = useChatStore()
      chatStore.messages = [
        {
          id: '1',
          role: 'assistant',
          content: '```javascript\nconsole.log("Hello");\n```',
          timestamp: new Date()
        }
      ]

      const wrapper = mount(MessageList)

      // 检查代码块相关元素
      expect(wrapper.html()).toContain('code-block-wrapper')
      expect(wrapper.html()).toContain('copy-button')
    })
  })

  describe('消息显示', () => {
    it('应该显示多条消息', () => {
      const chatStore = useChatStore()
      chatStore.messages = [
        {
          id: '1',
          role: 'user',
          content: '用户消息 1',
          timestamp: new Date()
        },
        {
          id: '2',
          role: 'assistant',
          content: '助手消息 1',
          timestamp: new Date()
        },
        {
          id: '3',
          role: 'user',
          content: '用户消息 2',
          timestamp: new Date()
        }
      ]

      const wrapper = mount(MessageList)
      const messageWrappers = wrapper.findAll('.message-wrapper')

      expect(messageWrappers.length).toBe(3)
    })

    it('应该正确区分用户和助手消息的样式', () => {
      const chatStore = useChatStore()
      chatStore.messages = [
        {
          id: '1',
          role: 'user',
          content: '用户消息',
          timestamp: new Date()
        },
        {
          id: '2',
          role: 'assistant',
          content: '助手消息',
          timestamp: new Date()
        }
      ]

      const wrapper = mount(MessageList)

      expect(wrapper.find('.message-user').exists()).toBe(true)
      expect(wrapper.find('.message-assistant').exists()).toBe(true)
    })

    it('应该显示时间戳', () => {
      const chatStore = useChatStore()
      const now = new Date()
      chatStore.messages = [
        {
          id: '1',
          role: 'user',
          content: '测试消息',
          timestamp: now
        }
      ]

      const wrapper = mount(MessageList)
      expect(wrapper.find('.message-time').exists()).toBe(true)
    })
  })

  describe('加载状态', () => {
    it('应该显示加载动画', () => {
      const chatStore = useChatStore()
      chatStore.isLoading = true
      // 添加一个空的助手消息来显示加载动画
      chatStore.messages = [
        {
          id: 'loading-msg',
          role: 'assistant',
          content: '',  // 空内容会显示加载动画
          timestamp: new Date()
        }
      ]

      const wrapper = mount(MessageList)
      expect(wrapper.find('.loading').exists()).toBe(true)
    })

    it('加载时不应显示空状态', () => {
      const chatStore = useChatStore()
      chatStore.isLoading = true
      chatStore.messages = [
        {
          id: 'loading-msg',
          role: 'assistant',
          content: '',
          timestamp: new Date()
        }
      ]

      const wrapper = mount(MessageList)
      expect(wrapper.find('.empty-state').exists()).toBe(false)
    })
  })

  describe('空状态', () => {
    it('应该在没有消息且未加载时显示空状态', () => {
      const chatStore = useChatStore()
      chatStore.messages = []
      chatStore.isLoading = false

      const wrapper = mount(MessageList)
      expect(wrapper.find('.empty-state').exists()).toBe(true)
      expect(wrapper.text()).toContain('开始新对话')
    })

    it('有消息时不应显示空状态', () => {
      const chatStore = useChatStore()
      chatStore.messages = [
        {
          id: '1',
          role: 'user',
          content: '测试消息',
          timestamp: new Date()
        }
      ]
      chatStore.isLoading = false

      const wrapper = mount(MessageList)
      expect(wrapper.find('.empty-state').exists()).toBe(false)
    })
  })

  describe('时间格式化', () => {
    it('应该正确格式化最近的消息为"刚刚"', () => {
      const chatStore = useChatStore()
      chatStore.messages = [
        {
          id: '1',
          role: 'user',
          content: '测试',
          timestamp: new Date()
        }
      ]

      const wrapper = mount(MessageList)
      expect(wrapper.find('.message-time').text()).toContain('刚刚')
    })
  })

  describe('思维链显示', () => {
    it('应该显示思维链内容（如果有）', () => {
      const chatStore = useChatStore()
      chatStore.messages = [
        {
          id: '1',
          role: 'assistant',
          content: '这是最终答案',
          reasoningContent: '这是思考过程',
          timestamp: new Date()
        }
      ]

      const wrapper = mount(MessageList)
      expect(wrapper.find('.reasoning-section').exists()).toBe(true)
      expect(wrapper.find('.reasoning-content').exists()).toBe(true)
      expect(wrapper.text()).toContain('思考过程')
    })

    it('思维链区域应该可以展开和折叠', async () => {
      const chatStore = useChatStore()
      chatStore.messages = [
        {
          id: '1',
          role: 'assistant',
          content: '答案',
          reasoningContent: '思考过程',
          timestamp: new Date()
        }
      ]

      const wrapper = mount(MessageList)
      const header = wrapper.find('.reasoning-header')
      const toggle = wrapper.find('.reasoning-toggle')

      // 初始状态应该是展开的（显示 ▼）
      expect(toggle.text()).toBe('▼')

      // 点击折叠
      await header.trigger('click')
      await nextTick()
      // 重新获取 toggle 元素
      expect(wrapper.find('.reasoning-toggle').text()).toBe('▶')

      // 再次点击展开
      await header.trigger('click')
      await nextTick()
      expect(wrapper.find('.reasoning-toggle').text()).toBe('▼')
    })

    it('没有思维链时不应该显示思维链区域', () => {
      const chatStore = useChatStore()
      chatStore.messages = [
        {
          id: '1',
          role: 'assistant',
          content: '只有答案，没有思考过程',
          timestamp: new Date()
        }
      ]

      const wrapper = mount(MessageList)
      expect(wrapper.find('.reasoning-section').exists()).toBe(false)
    })

    it('用户消息不应该有思维链显示', () => {
      const chatStore = useChatStore()
      chatStore.messages = [
        {
          id: '1',
          role: 'user',
          content: '用户消息',
          reasoningContent: '不应该显示这个',
          timestamp: new Date()
        }
      ]

      const wrapper = mount(MessageList)
      expect(wrapper.find('.reasoning-section').exists()).toBe(false)
    })

    it('思维链内容应该使用 Markdown 渲染', () => {
      const chatStore = useChatStore()
      chatStore.messages = [
        {
          id: '1',
          role: 'assistant',
          content: '答案',
          reasoningContent: '**思考**：`代码`',
          timestamp: new Date()
        }
      ]

      const wrapper = mount(MessageList)
      const reasoningContent = wrapper.find('.reasoning-content')
      expect(reasoningContent.html()).toContain('<strong>')
      expect(reasoningContent.html()).toContain('<code>')
    })
  })
})
