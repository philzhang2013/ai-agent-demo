import type { Message, ToolMessage, Tool } from '../types.js';

/**
 * 函数调用参数属性
 */
export interface FunctionProperty {
  type: string;
  description: string;
}

/**
 * 函数定义
 */
export interface FunctionDefinition {
  name: string;
  description: string;
  parameters: {
    type: string;
    properties: Record<string, FunctionProperty>;
    required?: string[];
  };
}

/**
 * 工具调用
 */
export interface ToolCall {
  id?: string;
  type: 'function';
  function: {
    name: string;
    arguments: string;
  };
}

/**
 * 聊天请求参数
 */
export interface ChatParams {
  model: string;
  messages: (Message | ToolMessage)[];
  stream?: boolean;
  tools?: Array<{ type: 'function'; function: FunctionDefinition }>;
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
  tool_calls?: ToolCall[];
  usage?: TokenUsage;
}

/**
 * LLM 客户端接口
 * 所有提供商适配器必须实现此接口
 */
export interface LLMClient {
  chat(params: ChatParams): Promise<ChatResponse>;
}
