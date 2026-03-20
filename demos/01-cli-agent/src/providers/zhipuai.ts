import type { LLMClient, ChatParams, ChatResponse, ToolCall } from './base.js';
import { logger, formatJSON } from '../logger.js';

/**
 * 智谱 AI 客户端适配器
 * 支持 Function Calling API
 */
export class ZhipuClient implements LLMClient {
  private apiKey: string;
  private baseURL: string;

  constructor(apiKey: string, baseURL?: string) {
    this.apiKey = apiKey;
    // 支持 CodePlan 专用端点或普通端点
    this.baseURL = baseURL || 'https://open.bigmodel.cn/api/paas/v4';
  }

  async chat(params: ChatParams): Promise<ChatResponse> {
    const url = `${this.baseURL}/chat/completions`;

    logger.debug('ZHIPUAI', `📡 请求端点: ${url}`);
    logger.debug('ZHIPUAI', `🤖 模型: ${params.model}`);

    // 转换消息格式（Function Calling 兼容）
    const messages = params.messages.map(m => {
      // 处理工具调用消息
      if ((m as any).tool_calls) {
        return {
          role: m.role,
          tool_calls: (m as any).tool_calls,
          content: null
        };
      }

      // 处理工具结果消息
      if ((m as any).tool_call_id || (m as any).role === 'tool') {
        return {
          role: 'tool',
          tool_call_id: (m as any).tool_call_id || '',
          content: m.content
        };
      }

      // 普通消息
      const msg: any = {
        role: m.role,
        content: m.content
      };

      return msg;
    });

    logger.debug('ZHIPUAI', `📤 消息数量: ${messages.length}`);

    // 构建请求体
    const requestBody: any = {
      model: params.model,
      messages: messages,
      stream: params.stream ?? false
    };

    // 添加工具定义（如果有）
    if (params.tools && params.tools.length > 0) {
      requestBody.tools = params.tools;
      logger.debug('ZHIPUAI', `🛠️  工具数量: ${params.tools.length}`);
    }

    logger.debug('ZHIPUAI', `📦 请求体: ${formatJSON(requestBody, 0)}`);

    try {
      const startTime = Date.now();
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify(requestBody)
      });

      const duration = Date.now() - startTime;
      logger.debug('ZHIPUAI', `⏱️  响应时间: ${duration}ms`);

      if (!response.ok) {
        const errorText = await response.text();
        logger.error('ZHIPUAI', `❌ HTTP ${response.status}: ${errorText}`);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data: any = await response.json();

      // 检查 API 错误
      if (data.error) {
        logger.error('ZHIPUAI', `❌ API 错误 [${data.error.code}]: ${data.error.message}`);
        throw new Error(`智谱 AI 错误 [${data.error.code}]: ${data.error.message}`);
      }

      // 提取响应内容
      const choice = data.choices?.[0];
      const message = choice?.message || {};

      // 提取文本内容
      const content = message.content || '';

      // 提取工具调用
      let toolCalls: ToolCall[] | undefined;
      if (message.tool_calls && Array.isArray(message.tool_calls) && message.tool_calls.length > 0) {
        toolCalls = message.tool_calls.map((tc: any) => ({
          id: tc.id,
          type: 'function' as const,
          function: {
            name: tc.function.name,
            arguments: tc.function.arguments
          }
        }));
        if (toolCalls) {
          logger.debug('ZHIPUAI', `🔧 工具调用: ${JSON.stringify(toolCalls.map(tc => tc.function.name))}`);
        }
      }

      // 提取 Token 使用
      const usage = data.usage ? {
        prompt_tokens: data.usage.prompt_tokens,
        completion_tokens: data.usage.completion_tokens,
        total_tokens: data.usage.total_tokens
      } : undefined;

      logger.debug('ZHIPUAI', `📊 Token: ${formatJSON(usage)}`);

      return { content, tool_calls: toolCalls || [], usage };
    } catch (error: any) {
      logger.error('ZHIPUAI', `💥 调用异常: ${error.message}`);
      throw new Error(`智谱 AI 调用失败: ${error.message}`);
    }
  }
}
