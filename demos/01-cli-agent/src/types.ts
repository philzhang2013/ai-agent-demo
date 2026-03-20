// ========== 类型定义 ==========

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
  apiKey: string;
  maxIterations?: number;
  mockMode?: boolean;
}
