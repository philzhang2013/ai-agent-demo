import type { LLMClient, ChatParams, ChatResponse, TokenUsage } from './base.js';

/**
 * MiniMax OpenAI 兼容 API 响应格式
 */
interface MinimaxCNResponse {
  choices?: Array<{
    message: {
      content: string;
      role: string;
    };
    finish_reason: string;
    index: number;
  }>;
  usage?: {
    total_tokens: number;
    prompt_tokens: number;
    completion_tokens: number;
  };
  error?: {
    message: string;
    type: string;
  };
}

/**
 * MiniMax 客户端适配器
 * 使用 OpenAI 兼容 API (api.minimaxi.com/v1)
 */
export class MinimaxClient implements LLMClient {
  private apiKey: string;
  private baseURL: string;

  constructor(apiKey: string, baseURL?: string) {
    this.apiKey = apiKey;
    // 使用中文平台端点（OpenAI 兼容）
    this.baseURL = baseURL || 'https://api.minimaxi.com';
  }

  async chat(params: ChatParams): Promise<ChatResponse> {
    // OpenAI 兼容端点
    const url = `${this.baseURL}/v1/chat/completions`;

    // 转换消息格式（OpenAI 兼容）
    const messages = params.messages.map(m => {
      const msg: any = {
        role: m.role === 'function' ? 'user' : m.role,
        content: m.content
      };

      // 如果是工具调用结果，添加名称标识
      if (m.role === 'function') {
        msg.content = `工具 ${(m as any).name} 的执行结果：${m.content}`;
      }

      return msg;
    });

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: params.model,
          messages: messages,
          stream: false
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data: MinimaxCNResponse = await response.json() as MinimaxCNResponse;

      // 检查 API 错误
      if (data.error) {
        throw new Error(`MiniMax API 错误: ${data.error.message}`);
      }

      // 提取响应内容
      const content = data.choices?.[0]?.message?.content || '';

      // 提取 Token 使用
      const usage: TokenUsage | undefined = data.usage
        ? {
            prompt_tokens: data.usage.prompt_tokens,
            completion_tokens: data.usage.completion_tokens,
            total_tokens: data.usage.total_tokens
          }
        : undefined;

      return { content, usage };
    } catch (error: any) {
      throw new Error(`MiniMax API 调用失败: ${error.message}`);
    }
  }
}
