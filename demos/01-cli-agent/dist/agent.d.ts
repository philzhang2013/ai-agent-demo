import type { Message, ToolMessage, AgentOptions } from './types.js';
/**
 * AI Agent 类
 * 负责与 LLM 交互，处理工具调用，管理对话状态
 */
export declare class Agent {
    private client;
    private messages;
    private maxIterations;
    private iterationCount;
    private mockMode;
    constructor(options: AgentOptions);
    /**
     * 获取系统提示词
     */
    private getSystemPrompt;
    /**
     * 解析 LLM 响应中的工具调用
     */
    private parseToolCall;
    /**
     * 执行工具调用
     */
    private executeTool;
    /**
     * 调用 LLM API
     */
    private callLLM;
    /**
     * 模拟 LLM 响应（用于测试）
     */
    private mockLLMResponse;
    /**
     * 解析数学表达式（支持中文运算符）
     */
    private parseMathExpression;
    /**
     * 处理用户输入
     */
    processUserInput(userInput: string): Promise<string>;
    /**
     * 获取消息历史
     */
    getMessages(): (Message | ToolMessage)[];
    /**
     * 重置消息历史（保留系统提示）
     */
    resetHistory(): void;
    /**
     * 检查是否为模拟模式
     */
    isMockMode(): boolean;
}
//# sourceMappingURL=agent.d.ts.map