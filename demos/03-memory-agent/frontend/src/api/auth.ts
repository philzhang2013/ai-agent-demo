/**
 * 认证 API 客户端
 */
import type { AuthResponse, RegisterRequest, LoginRequest } from './types'

const BASE_URL = '/api/auth'

export class AuthAPI {
  /**
   * 用户注册
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await fetch(`${BASE_URL}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '注册失败')
    }

    return response.json()
  }

  /**
   * 用户登录
   */
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await fetch(`${BASE_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '登录失败')
    }

    return response.json()
  }

  /**
   * 退出登录（前端实现）
   */
  logout(): void {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  /**
   * 保存认证信息
   */
  saveAuth(authResponse: AuthResponse): void {
    localStorage.setItem('token', authResponse.token)
    localStorage.setItem('user', JSON.stringify(authResponse.user))
  }

  /**
   * 获取保存的 token
   */
  getToken(): string | null {
    return localStorage.getItem('token')
  }

  /**
   * 获取保存的用户信息
   */
  getUser(): AuthResponse['user'] | null {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      return JSON.parse(userStr)
    }
    return null
  }

  /**
   * 检查是否已登录
   */
  isAuthenticated(): boolean {
    return !!this.getToken()
  }
}

// 导出单例
export const authAPI = new AuthAPI()
