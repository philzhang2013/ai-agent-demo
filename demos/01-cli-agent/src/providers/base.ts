import type { Message, ToolMessage } from '../types.js';

/**
 * 聊天请求参数
 */
export interface ChatParams {
  model: string;
  messages: (Message | ToolMessage)[];
  stream?: boolean;
}

/**
 * Token 使用统计
 */
export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

/**
 * 聊天响应
 */
export interface ChatResponse {
  content: string;
  usage?: TokenUsage;
}

/**
 * LLM 客户端接口
 * 所有提供商适配器必须实现此接口
 */
export interface LLMClient {
  chat(params: ChatParams): Promise<ChatResponse>;
}
