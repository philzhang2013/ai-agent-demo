import { ZhipuAI } from 'zhipuai-sdk-nodejs-v4';
import type { Message, ToolMessage, ToolCall, AgentOptions } from './types.js';
import { tools, getToolDescriptions, findTool } from './tools.js';

// ========== Agent 类 ==========

/**
 * AI Agent 类
 * 负责与 LLM 交互，处理工具调用，管理对话状态
 */
export class Agent {
  private client: ZhipuAI | null;
  private messages: (Message | ToolMessage)[] = [];
  private maxIterations: number;
  private iterationCount: number = 0;
  private mockMode: boolean;

  constructor(options: AgentOptions) {
    this.maxIterations = options.maxIterations ?? 5;
    this.mockMode = options.mockMode ?? false;

    if (this.mockMode) {
      this.client = null;
      console.log('🧪 Agent 运行在模拟模式（不会调用真实 API）');
    } else {
      this.client = new ZhipuAI({ apiKey: options.apiKey });
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
      const data = await this.client.createCompletions({
        model: 'glm-4',
        messages: this.messages.map(m => ({
          role: m.role,
          content: m.content,
          ...(m.role === 'function' && { name: (m as ToolMessage).name })
        })),
        stream: false
      }) as any;

      if (data.choices && data.choices[0]) {
        return data.choices[0].message.content || '';
      }

      throw new Error('LLM 返回空响应');
    } catch (error) {
      console.error('LLM 调用错误:', error);
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
    this.messages.push({ role: 'user', content: userInput });

    while (this.iterationCount < this.maxIterations) {
      this.iterationCount++;

      if (!this.mockMode) {
        console.log(`\n🔄 [Agent 迭代 ${this.iterationCount}]`);
      }

      // 调用 LLM
      const response = await this.callLLM();

      // 检查是否需要调用工具
      const toolCall = this.parseToolCall(response);

      if (toolCall) {
        if (!this.mockMode) {
          console.log(`📋 思考: 需要调用工具 "${toolCall.name}"`);
          console.log(`📝 参数: ${JSON.stringify(toolCall.arguments)}`);
        }

        // 执行工具
        const result = await this.executeTool(toolCall.name, toolCall.arguments);

        if (!this.mockMode) {
          console.log(`✅ 工具结果: ${result}`);
        }

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

        continue; // 继续循环，让 LLM 基于工具结果生成最终回复
      }

      // 返回最终回复
      return response;
    }

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
}
