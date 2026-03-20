import type { LLMClient, ChatParams, ChatResponse } from './base.js';
import { logger, formatJSON } from '../logger.js';

/**
 * 智谱 AI 客户端适配器
 * 支持普通 API 和 CodePlan API
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

    // 转换消息格式（智谱 OpenAI 兼容格式）
    const messages = params.messages.map(m => {
      const msg: any = {
        role: m.role === 'function' ? 'user' : m.role,
        content: m.content
      };

      // 如果是工具调用结果，添加名称
      if (m.role === 'function') {
        msg.name = (m as any).name;
        msg.content = `工具 ${(m as any).name} 的执行结果：${m.content}`;
      }

      return msg;
    });

    logger.debug('ZHIPUAI', `📤 消息数量: ${messages.length}`);

    const requestBody = {
      model: params.model,
      messages: messages,
      stream: params.stream ?? false
    };

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
      const content = data.choices?.[0]?.message?.content || '';
      logger.debug('ZHIPUAI', `📥 响应内容: ${content.substring(0, 100)}...`);

      // 提取 Token 使用
      const usage = data.usage ? {
        prompt_tokens: data.usage.prompt_tokens,
        completion_tokens: data.usage.completion_tokens,
        total_tokens: data.usage.total_tokens
      } : undefined;

      logger.debug('ZHIPUAI', `📊 Token: ${formatJSON(usage)}`);

      return { content, usage };
    } catch (error: any) {
      logger.error('ZHIPUAI', `💥 调用异常: ${error.message}`);
      throw new Error(`智谱 AI 调用失败: ${error.message}`);
    }
  }
}
