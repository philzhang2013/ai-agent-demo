import { ZhipuClient } from './zhipuai.js';
import { MinimaxClient } from './minimax.js';
import { KimiClient } from './kimi.js';

/**
 * 支持的 LLM 提供商
 */
export enum LLMProvider {
  ZHIPUAI = 'zhipuai',
  MINIMAX = 'minimax',
  KIMI = 'kimi'
}

/**
 * 创建 LLM 客户端实例（工厂函数）
 */
export function createClient(
  provider: LLMProvider,
  apiKey: string,
  baseURL?: string
) {
  switch (provider) {
    case LLMProvider.ZHIPUAI:
      return new ZhipuClient(apiKey, baseURL);
    case LLMProvider.MINIMAX:
      return new MinimaxClient(apiKey, baseURL);
    case LLMProvider.KIMI:
      return new KimiClient(apiKey, baseURL);
    default:
      throw new Error(`不支持的提供商: ${provider}`);
  }
}

// 导出类型
export type { LLMClient, ChatParams, ChatResponse, TokenUsage, FunctionDefinition, ToolCall } from './base.js';
