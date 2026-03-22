/**
 * 聊天 API 客户端
 * 支持 SSE 流式输出
 */
import type { SSEEvent } from './types'

export class ChatAPI {
  private baseURL = '/api/chat'

  /**
   * 发送消息（非流式）
   */
  async sendMessage(message: string, sessionId?: string): Promise<{
    response: string
    session_id: string
  }> {
    const response = await fetch(this.baseURL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message,
        session_id: sessionId
      })
    })

    if (!response.ok) {
      throw new Error(`API 错误: ${response.status}`)
    }

    return response.json()
  }

  /**
   * 发送消息（SSE 流式）
   */
  sendMessageStream(
    message: string,
    onEvent: (event: SSEEvent) => void,
    sessionId?: string
  ): () => void {
    const url = `${this.baseURL}/stream`

    // 使用 EventSource 连接
    // 注意：由于 SSE 需要发送 POST 数据，这里使用 fetch + ReadableStream
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message,
        session_id: sessionId
      })
    }).then(async (response) => {
      if (!response.ok) {
        onEvent({
          type: 'error',
          error: `HTTP ${response.status}`
        })
        return
      }

      const reader = response.body?.getReader()
      if (!reader) {
        onEvent({
          type: 'error',
          error: '无法读取响应流'
        })
        return
      }

      const decoder = new TextDecoder()
      let buffer = ''
      let currentEvent = ''

      try {
        while (true) {
          const { done, value } = await reader.read()

          if (done) break

          buffer += decoder.decode(value, { stream: true })

          // 处理 SSE 格式
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            const trimmedLine = line.trim()

            // 解析 event 类型（如: event: token）
            if (trimmedLine.startsWith('event: ')) {
              currentEvent = trimmedLine.slice(7).trim()
            }
            // 解析 data 内容（如: data: {"content": "用户"}）
            else if (trimmedLine.startsWith('data: ')) {
              const data = trimmedLine.slice(6).trim()

              if (data === '[DONE]') {
                onEvent({ type: 'done' })
                currentEvent = ''
                continue
              }

              try {
                const eventData = JSON.parse(data)
                // 将 event 类型添加到数据中
                const sseEvent = {
                  type: currentEvent || 'token',
                  ...eventData
                }
                onEvent(sseEvent)
              } catch (e) {
                console.error('解析 SSE 数据失败:', e, data)
              }

              currentEvent = ''
            }
          }
        }
      } catch (e) {
        onEvent({
          type: 'error',
          error: e instanceof Error ? e.message : '未知错误'
        })
      }
    })

    // 返回取消函数
    return () => {
      // 实际实现中应该可以取消请求
    }
  }
}

// 导出单例
export const chatAPI = new ChatAPI()
