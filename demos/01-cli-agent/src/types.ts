// ========== 类型定义 ==========

// 先导入类型再使用
import { LLMProvider } from './providers/index.js';

// 重新导出提供商类型
export { LLMProvider, type LLMClient, type ChatParams, type ChatResponse } from './providers/index.js';

/**
 * 对话消息
 */
export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

/**
 * 工具执行结果消息
 */
export interface ToolMessage {
  role: 'function';
  content: string;
  name: string;
}

/**
 * 工具调用信息
 */
export interface ToolCall {
  name: string;
  arguments: Record<string, any>;
}

/**
 * 工具定义
 */
export interface Tool {
  name: string;
  description: string;
  parameters: {
    type: string;
    properties: Record<string, any>;
    required?: string[];
  };
  execute: (args: Record<string, any>) => Promise<string> | string;
}

/**
 * Agent 配置选项
 */
export interface AgentOptions {
  // 新的多提供商配置
  provider?: LLMProvider;
  apiKey?: string;
  baseURL?: string;
  model?: string;

  // 向后兼容的配置
  maxIterations?: number;
  mockMode?: boolean;
}
