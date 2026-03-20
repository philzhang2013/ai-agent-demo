import { createClient, LLMProvider, type LLMClient } from './providers/index.js';
import type { Message, ToolMessage, ToolCall, AgentOptions } from './types.js';
import { tools, getToolDescriptions, findTool } from './tools.js';
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
   * 获取系统提示词
   */
  private getSystemPrompt(): string {
    const toolDescriptions = getToolDescriptions();

    return `你是一个智能 AI 助手，可以帮助用户回答问题并使用工具完成任务。

可用的工具:
${toolDescriptions}

当需要使用工具时，请按以下格式返回:
TOOL_CALL: <工具名称>
ARGUMENTS: <JSON 格式的参数>

例如:
TOOL_CALL: calculator
ARGUMENTS: {"expression": "18 + 25"}

工具调用结果会自动添加到对话中，请根据结果给用户一个友好的回复。

请用中文回复用户。`;
  }

  /**
   * 解析 LLM 响应中的工具调用
   */
  private parseToolCall(content: string): ToolCall | null {
    const toolCallMatch = content.match(/TOOL_CALL:\s*(\w+)/);
    const argsMatch = content.match(/ARGUMENTS:\s*(\{.*\})/);

    if (toolCallMatch && argsMatch) {
      try {
        return {
          name: toolCallMatch[1],
          arguments: JSON.parse(argsMatch[1])
        };
      } catch {
        return null;
      }
    }
    return null;
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
   * 调用 LLM API
   */
  private async callLLM(): Promise<string> {
    // 模拟模式返回预设响应
    if (this.mockMode) {
      return this.mockLLMResponse();
    }

    if (!this.client) {
      throw new Error('LLM 客户端未初始化');
    }

    try {
      // 使用统一的适配器接口
      const response = await this.client.chat({
        model: this.model,
        messages: this.messages,
        stream: false
      });

      if (!response.content) {
        throw new Error('LLM 返回空响应');
      }

      // 日志: Token 使用情况
      if (response.usage) {
        logger.info('TOKEN', `📊 Token 使用: 输入=${response.usage.prompt_tokens}, 输出=${response.usage.completion_tokens}, 总计=${response.usage.total_tokens}`);
      }

      return response.content;
    } catch (error: any) {
      logger.error('LLM', `❌ API 调用失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 模拟 LLM 响应（用于测试）
   */
  private mockLLMResponse(): string {
    const lastMessage = this.messages[this.messages.length - 1];

    if (lastMessage.role === 'function') {
      // 如果最后一条是工具结果，返回友好的回复
      const toolName = (lastMessage as ToolMessage).name;
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
      return `TOOL_CALL: calculator\nARGUMENTS: {"expression": "${expr}"}`;
    }

    // 检查是否是天气查询
    if (userContent.includes('天气') || userContent.includes('气温')) {
      // 提取城市名称
      const cities = ['北京', '上海', '深圳', '广州'];
      const city = cities.find(c => userContent.includes(c)) || '北京';
      return `TOOL_CALL: get_weather\nARGUMENTS: {"city": "${city}"}`;
    }

    return '我是模拟模式下的 AI 助手。你可以让我进行数学计算（如"计算 18 + 25"）或查询天气（如"北京天气"）。';
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
   * 处理用户输入
   */
  async processUserInput(userInput: string): Promise<string> {
    this.iterationCount = 0;

    // 日志: 开始处理用户输入
    logger.info('AGENT', separator('═', 60));
    logger.info('AGENT', `👤 用户输入: ${userInput}`);

    // 添加用户消息到历史
    this.messages.push({ role: 'user', content: userInput });
    logger.debug('MEMORY', `消息历史长度: ${this.messages.length} 条`);

    while (this.iterationCount < this.maxIterations) {
      this.iterationCount++;

      logger.info('AGENT', separator('─', 40));
      logger.info('AGENT', `🔄 第 ${this.iterationCount} 次迭代`);

      // 日志: 发送给 LLM 的消息
      logger.debug('LLM', '📤 发送请求到 LLM:');
      logger.debug('LLM', formatMessages(this.messages));

      // 调用 LLM
      const response = await this.callLLM();

      // 日志: LLM 响应
      logger.debug('LLM', '📥 收到 LLM 响应:');
      logger.debug('LLM', `  ${response.substring(0, 200)}${response.length > 200 ? '...' : ''}`);

      // 检查是否需要调用工具
      const toolCall = this.parseToolCall(response);

      if (toolCall) {
        logger.info('AGENT', `🔧 识别工具调用: ${toolCall.name}`);
        logger.info('AGENT', `📋 参数: ${formatJSON(toolCall.arguments)}`);

        // 执行工具
        logger.info('TOOL', `⚙️  执行工具: ${toolCall.name}`);
        const result = await this.executeTool(toolCall.name, toolCall.arguments);

        logger.success('TOOL', `✨ 工具结果: ${result}`);

        // 添加工具结果到消息历史
        this.messages.push({
          role: 'assistant',
          content: response
        });
        this.messages.push({
          role: 'function',
          content: result,
          name: toolCall.name
        });

        logger.debug('MEMORY', `📝 已添加工具结果到历史，当前消息数: ${this.messages.length}`);

        continue; // 继续循环，让 LLM 基于工具结果生成最终回复
      }

      // 返回最终回复
      logger.success('AGENT', `✅ 最终回复: ${response.substring(0, 100)}${response.length > 100 ? '...' : ''}`);
      logger.info('AGENT', separator('═', 60));
      return response;
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
