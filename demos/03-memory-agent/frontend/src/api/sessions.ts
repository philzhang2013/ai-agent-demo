/**
 * 会话 API 客户端
 * 管理会话列表、创建、删除、更新标题等
 */
import type { ChatMessage } from './types'

/**
 * 会话接口（用于列表显示）
 */
export interface Session {
  id: string
  user_id: string
  title: string
  last_message?: string
  message_count?: number
  created_at: string
  updated_at: string
}

/**
 * 会话详情（含消息列表）
 */
export interface SessionDetail extends Session {
  messages: ChatMessage[]
}

/**
 * 创建会话请求
 */
interface CreateSessionRequest {
  // 创建会话不需要额外参数
}

/**
 * 更新标题请求
 */
interface UpdateTitleRequest {
  title: string
}

export class SessionsAPI {
  private baseURL = '/api/sessions'

  /**
   * 获取 token（从 localStorage）
   */
  private getToken(): string | null {
    return localStorage.getItem('token')
  }

  /**
   * 获取认证头
   */
  private getAuthHeaders(): HeadersInit {
    const token = this.getToken()
    const headers: HeadersInit = {
      'Content-Type': 'application/json'
    }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    return headers
  }

  /**
   * 获取会话列表（含预览信息）
   */
  async getSessions(): Promise<Session[]> {
    const response = await fetch(this.baseURL, {
      method: 'GET',
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error(`获取会话列表失败: ${response.status}`)
    }

    return response.json()
  }

  /**
   * 获取会话详情（含消息）
   */
  async getSession(sessionId: string): Promise<SessionDetail> {
    const response = await fetch(`${this.baseURL}/${sessionId}`, {
      method: 'GET',
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error(`获取会话详情失败: ${response.status}`)
    }

    return response.json()
  }

  /**
   * 创建新会话
   */
  async createSession(): Promise<Session> {
    const response = await fetch(this.baseURL, {
      method: 'POST',
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error(`创建会话失败: ${response.status}`)
    }

    return response.json()
  }

  /**
   * 删除会话
   */
  async deleteSession(sessionId: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/${sessionId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error(`删除会话失败: ${response.status}`)
    }
  }

  /**
   * 更新会话标题
   */
  async updateSessionTitle(sessionId: string, title: string): Promise<Session> {
    const response = await fetch(`${this.baseURL}/${sessionId}/title`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ title } as UpdateTitleRequest)
    })

    if (!response.ok) {
      throw new Error(`更新会话标题失败: ${response.status}`)
    }

    return response.json()
  }
}

// 导出单例
export const sessionsAPI = new SessionsAPI()
