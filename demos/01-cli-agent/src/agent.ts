import { createClient, LLMProvider, type LLMClient, type FunctionDefinition, type ToolCall as ProviderToolCall } from './providers/index.js';
import type { Message, ToolMessage, ToolCall, AgentOptions } from './types.js';
import { tools, findTool } from './tools.js';
import { logger, formatMessages, separator, formatJSON } from './logger.js';

// 默认模型配置
const DEFAULT_MODELS: Record<LLMProvider, string> = {
  [LLMProvider.ZHIPUAI]: 'glm-5',
  [LLMProvider.MINIMAX]: 'M2-her',
  [LLMProvider.KIMI]: 'moonshot-v1-8k'
};

// ========== Agent 类 ==========

/**
 * AI Agent 类
 * 负责与 LLM 交互，处理工具调用，管理对话状态
 */
export class Agent {
  private client: LLMClient | null;
  private messages: (Message | ToolMessage)[] = [];
  private maxIterations: number;
  private iterationCount: number = 0;
  private mockMode: boolean;
  private provider: LLMProvider;
  private model: string;

  constructor(options: AgentOptions) {
    // 默认使用智谱 AI（向后兼容）
    this.provider = options.provider ?? LLMProvider.ZHIPUAI;
    this.model = options.model ?? DEFAULT_MODELS[this.provider];
    this.maxIterations = options.maxIterations ?? 5;
    this.mockMode = options.mockMode ?? false;

    if (this.mockMode) {
      this.client = null;
      process.stderr.write('🧪 Agent 运行在模拟模式（不会调用真实 API）\n');
    } else {
      // 验证 API Key
      if (!options.apiKey) {
        throw new Error(`未提供 ${this.provider} 的 API Key`);
      }

      // 使用工厂创建客户端
      this.client = createClient(this.provider, options.apiKey, options.baseURL);
      process.stderr.write(`🔌 已连接到 ${this.provider} (模型: ${this.model})\n`);
    }

    this.messages.push({
      role: 'system',
      content: this.getSystemPrompt()
    });
  }

  /**
   * 获取系统提示词（Function Calling 模式）
   */
  private getSystemPrompt(): string {
    return `你是一个智能 AI 劏手，可以帮助用户回答问题并使用工具完成任务。

工具调用结果会自动添加到对话中，请根据结果给用户一个友好的回复。

请用中文回复用户。`;
  }

  /**
   * 将工具转换为 Function Calling 格式
   */
  private getToolDefinitions(): Array<{ type: 'function'; function: FunctionDefinition }> {
    return tools.map(tool => ({
      type: 'function' as const,
      function: {
        name: tool.name,
        description: tool.description,
        parameters: {
          type: tool.parameters.type,
          properties: tool.parameters.properties as any,
          required: tool.parameters.required || []
        }
      }
    }));
  }

  /**
   * 执行工具调用
   */
  private async executeTool(name: string, args: Record<string, any>): Promise<string> {
    const tool = findTool(name);
    if (!tool) {
      return `错误: 找不到工具 "${name}"`;
    }
    return await tool.execute(args);
  }

  /**
   * 调用 LLM API（Function Calling 模式）
   */
  private async callLLM(): Promise<{ content: string; toolCalls?: ProviderToolCall[] }> {
    // 模拟模式返回预设响应
    if (this.mockMode) {
      const lastMessage = this.messages[this.messages.length - 1];

      // 检查是否是工具结果
      if ((lastMessage as any).role === 'tool' || lastMessage.role === 'function') {
        // 工具执行后，返回友好的最终回复
        const toolName = (lastMessage as any).tool_call_id ? this.getToolNameFromCallId((lastMessage as any).tool_call_id) : (lastMessage as ToolMessage).name;
        const result = lastMessage.content;

        if (toolName === 'calculator') {
          return { content: `计算结果: ${result}\n\n如果你还有其他计算需求，随时告诉我！` };
        }
        if (toolName === 'get_weather') {
          return { content: `${result}\n\n如果你想查询其他城市的天气，也可以告诉我！` };
        }
        return { content: `工具调用完成：${result}` };
      }

      // 分析用户输入并决定是否调用工具
      const userContent = lastMessage.content.toLowerCase();

      // 检查是否是计算请求
      if (userContent.includes('计算') || /\d+[\+\-\*\/]\d+/.test(userContent)) {
        const expr = this.parseMathExpression(userContent);
        return {
          content: '',
          toolCalls: [{
            type: 'function',
            function: {
              name: 'calculator',
              arguments: JSON.stringify({ expression: expr })
            }
          }]
        };
      }

      // 检查是否是天气查询
      if (userContent.includes('天气') || userContent.includes('气温')) {
        // 提取城市名称
        const cities = ['北京', '上海', '深圳', '广州'];
        const city = cities.find(c => userContent.includes(c)) || '北京';
        return {
          content: '',
          toolCalls: [{
            type: 'function',
            function: {
              name: 'get_weather',
              arguments: JSON.stringify({ city })
            }
          }]
        };
      }

      return { content: this.mockLLMResponse() };
    }

    if (!this.client) {
      throw new Error('LLM 客户端未初始化');
    }

    try {
      // 获取工具定义
      const toolDefinitions = this.getToolDefinitions();

      logger.debug('AGENT', `🛠️  工具定义: ${JSON.stringify(toolDefinitions.map(t => t.function.name))}`);

      // 使用统一的适配器接口，传递 tools 参数
      const response = await this.client.chat({
        model: this.model,
        messages: this.messages,
        tools: toolDefinitions,
        stream: false
      });

      if (!response.content && !response.tool_calls) {
        throw new Error('LLM 返回空响应');
      }

      // 日志: Token 使用情况
      if (response.usage) {
        logger.info('TOKEN', `📊 Token 使用: 输入=${response.usage.prompt_tokens}, 输出=${response.usage.completion_tokens}, 总计=${response.usage.total_tokens}`);
      }

      return {
        content: response.content || '',
        toolCalls: response.tool_calls
      };
    } catch (error: any) {
      logger.error('LLM', `❌ API 调用失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 模拟 LLM 响应（用于测试，Function Calling 模式）
   */
  private mockLLMResponse(): string {
    const lastMessage = this.messages[this.messages.length - 1];

    // 检查是否是工具结果
    if ((lastMessage as any).role === 'tool' || lastMessage.role === 'function') {
      const toolName = (lastMessage as any).tool_call_id ? this.getToolNameFromCallId((lastMessage as any).tool_call_id) : (lastMessage as ToolMessage).name;
      const result = lastMessage.content;

      if (toolName === 'calculator') {
        return `${result}\n\n如果你还有其他计算需求，随时告诉我！`;
      }
      if (toolName === 'get_weather') {
        return `${result}\n\n如果你想查询其他城市的天气，也可以告诉我！`;
      }
      return `工具调用完成：${result}`;
    }

    // 分析用户输入并决定是否调用工具
    const userContent = lastMessage.content.toLowerCase();

    // 检查是否是计算请求
    if (userContent.includes('计算') || /\d+[\+\-\*\/]\d+/.test(userContent)) {
      const expr = this.parseMathExpression(userContent);
      // 返回一个空响应，tool_calls 会在 callLLM 中构造
      return '';
    }

    // 检查是否是天气查询
    if (userContent.includes('天气') || userContent.includes('气温')) {
      // 返回一个空响应，tool_calls 会在 callLLM 中构造
      return '';
    }

    return '我是模拟模式下的 AI 助手。你可以让我进行数学计算（如"计算 18 + 25"）或查询天气（如"北京天气"）。';
  }

  /**
   * 从 tool_call_id 中提取工具名称（用于模拟模式）
   */
  private getToolNameFromCallId(callId: string): string {
    // 简单的实现，假设 callId 包含工具名称
    if (callId.includes('calculator')) return 'calculator';
    if (callId.includes('get_weather')) return 'get_weather';
    return 'unknown';
  }

  /**
   * 解析数学表达式（支持中文运算符）
   */
  private parseMathExpression(input: string): string {
    // 首先尝试匹配直接的数学表达式（如 "18 + 25"）
    const directMatch = input.match(/(\d+[\+\-\*\/\(\)\s\d]+)/);
    if (directMatch) {
      return directMatch[1].trim();
    }

    // 解析中文运算符
    let expr = input;

    // 处理中文运算符
    const replacements: [RegExp, string][] = [
      [/\s*除以\s*/g, ' / '],
      [/\*乘以\*/g, ' * '],
      [/\*乘\*/g, ' * '],
      [/\*加上\*/g, ' + '],
      [/\*加\*/g, ' + '],
      [/\*减去\*/g, ' - '],
      [/\*减\*/g, ' - '],
    ];

    for (const [pattern, replacement] of replacements) {
      expr = expr.replace(pattern, replacement);
    }

    // 提取数字和运算符
    const mathExprMatch = expr.match(/(\d+[\s\+\-\*\/\(\)\d]+)/);
    if (mathExprMatch) {
      return mathExprMatch[1].trim();
    }

    // 默认返回简单表达式
    return '1 + 1';
  }

  /**
   * 处理用户输入（Function Calling 模式）
   */
  async processUserInput(userInput: string): Promise<string> {
    this.iterationCount = 0;

    // 日志: 开始处理用户输入
    logger.info('AGENT', separator('═', 60));
    logger.info('AGENT', `👤 用户输入: ${userInput}`);

    // 添加用户消息到历史
    this.messages.push({ role: 'user', content: userInput });
    logger.debug('MEMORY', `消息历史长度: ${this.messages.length} 条`);
    logger.debug('MEMORY', `消息历史内容: ${JSON.stringify(this.messages)}`);

    while (this.iterationCount < this.maxIterations) {
      this.iterationCount++;

      logger.info('AGENT', separator('─', 40));
      logger.info('AGENT', `🔄 第 ${this.iterationCount} 次迭代`);

      // 日志: 发送给 LLM 的消息
      logger.debug('LLM', '📤 发送请求到 LLM:');
      logger.debug('LLM', formatMessages(this.messages));

      // 调用 LLM
      const { content, toolCalls } = await this.callLLM();

      // 日志: LLM 响应
      logger.debug('LLM', '📥 收到 LLM 响应:');
      if (toolCalls && toolCalls.length > 0) {
        logger.debug('LLM', `  工具调用: ${JSON.stringify(toolCalls)}`);
      } else {
        logger.debug('LLM', `  ${content.substring(0, 200)}${content.length > 200 ? '...' : ''}`);
      }

      // 检查是否有工具调用
      if (toolCalls && toolCalls.length > 0) {
        for (const toolCall of toolCalls) {
          const toolName = toolCall.function.name;
          let toolArgs: Record<string, any>;

          // 解析参数（可能是字符串或已解析的对象）
          try {
            toolArgs = typeof toolCall.function.arguments === 'string'
              ? JSON.parse(toolCall.function.arguments)
              : toolCall.function.arguments;
          } catch {
            logger.error('AGENT', `❌ 无法解析工具参数: ${toolCall.function.arguments}`);
            toolArgs = {};
          }

          logger.info('AGENT', `🔧 识别工具调用: ${toolName}`);
          logger.info('AGENT', `📋 参数: ${formatJSON(toolArgs)}`);

          // 执行工具
          logger.info('TOOL', `⚙️  执行工具: ${toolName}`);
          const result = await this.executeTool(toolName, toolArgs);

          logger.success('TOOL', `✨ 工具结果: ${result}`);

          // 添加工具调用到历史（Function Calling 格式）
          this.messages.push({
            role: 'assistant',
            content: content || '',
            tool_calls: [toolCall]
          } as any);

          // 添加工具结果到历史
          this.messages.push({
            role: 'tool',
            tool_call_id: toolCall.id || '',
            content: result
          } as any);

          logger.debug('MEMORY', `📝 已添加工具结果到历史，当前消息数: ${this.messages.length}`);
        }

        continue; // 继续循环，让 LLM 基于工具结果生成最终回复
      }

      // 返回最终回复
      logger.success('AGENT', `✅ 最终回复: ${content.substring(0, 100)}${content.length > 100 ? '...' : ''}`);
      logger.info('AGENT', separator('═', 60));
      return content;
    }

    logger.warning('AGENT', '⚠️  达到最大迭代次数');
    logger.info('AGENT', separator('═', 60));
    return '达到最大迭代次数，请重新尝试。';
  }

  /**
   * 获取消息历史
   */
  getMessages(): (Message | ToolMessage)[] {
    return [...this.messages];
  }

  /**
   * 重置消息历史（保留系统提示）
   */
  resetHistory(): void {
    this.messages = [{
      role: 'system',
      content: this.getSystemPrompt()
    }];
  }

  /**
   * 检查是否为模拟模式
   */
  isMockMode(): boolean {
    return this.mockMode;
  }

  /**
   * 获取当前提供商
   */
  getProvider(): LLMProvider {
    return this.provider;
  }

  /**
   * 获取当前模型
   */
  getModel(): string {
    return this.model;
  }
}
