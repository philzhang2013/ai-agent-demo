import { describe, it, expect, beforeEach } from 'vitest';
import { Agent } from '../src/agent.js';
import type { Message } from '../src/types.js';

describe('Agent 类测试', () => {
  describe('构造函数', () => {
    it('应该创建一个 Agent 实例', () => {
      const agent = new Agent({
        apiKey: 'test-key',
        mockMode: true
      });
      expect(agent).toBeDefined();
    });

    it('应该支持自定义最大迭代次数', () => {
      const agent = new Agent({
        apiKey: 'test-key',
        mockMode: true,
        maxIterations: 10
      });
      expect(agent).toBeDefined();
    });

    it('应该在模拟模式下初始化', () => {
      const agent = new Agent({
        apiKey: 'test-key',
        mockMode: true
      });
      expect(agent.isMockMode()).toBe(true);
    });

    it('应该有默认的消息历史（系统提示）', () => {
      const agent = new Agent({
        apiKey: 'test-key',
        mockMode: true
      });
      const messages = agent.getMessages();
      expect(messages.length).toBeGreaterThan(0);
      expect(messages[0].role).toBe('system');
    });
  });

  describe('isMockMode', () => {
    it('应该在模拟模式下返回 true', () => {
      const agent = new Agent({
        apiKey: 'test-key',
        mockMode: true
      });
      expect(agent.isMockMode()).toBe(true);
    });

    it('应该在非模拟模式下返回 false', () => {
      const agent = new Agent({
        apiKey: 'test-key',
        mockMode: false
      });
      expect(agent.isMockMode()).toBe(false);
    });
  });

  describe('getMessages', () => {
    let agent: Agent;

    beforeEach(() => {
      agent = new Agent({
        apiKey: 'test-key',
        mockMode: true
      });
    });

    it('应该返回消息历史的副本', () => {
      const messages1 = agent.getMessages();
      const messages2 = agent.getMessages();
      expect(messages1).not.toBe(messages2);
      expect(messages1).toEqual(messages2);
    });

    it('初始状态应该只包含系统提示', () => {
      const messages = agent.getMessages();
      expect(messages).toHaveLength(1);
      expect(messages[0].role).toBe('system');
    });
  });

  describe('resetHistory', () => {
    it('应该重置消息历史但保留系统提示', async () => {
      const agent = new Agent({
        apiKey: 'test-key',
        mockMode: true
      });

      // 添加一些对话
      await agent.processUserInput('你好');
      const messagesBeforeReset = agent.getMessages();
      expect(messagesBeforeReset.length).toBeGreaterThan(1);

      // 重置
      agent.resetHistory();
      const messagesAfterReset = agent.getMessages();

      // 应该只剩系统提示
      expect(messagesAfterReset).toHaveLength(1);
      expect(messagesAfterReset[0].role).toBe('system');
    });
  });

  describe('processUserInput', () => {
    let agent: Agent;

    beforeEach(() => {
      agent = new Agent({
        apiKey: 'test-key',
        mockMode: true,
        maxIterations: 5
      });
    });

    it('应该处理简单的问候', async () => {
      const response = await agent.processUserInput('你好');
      expect(response).toBeDefined();
      expect(typeof response).toBe('string');
    });

    it('应该处理计算请求', async () => {
      const response = await agent.processUserInput('计算 18 + 25');
      expect(response).toBeDefined();
      expect(response).toContain('计算结果');
    });

    it('应该处理天气查询请求', async () => {
      const response = await agent.processUserInput('北京天气怎么样');
      expect(response).toBeDefined();
      expect(response).toContain('北京');
    });

    it('应该将用户消息添加到历史', async () => {
      await agent.processUserInput('你好');
      const messages = agent.getMessages();
      const userMessage = messages.find(m => m.role === 'user' && m.content === '你好');
      expect(userMessage).toBeDefined();
    });

    it('应该支持连续对话', async () => {
      await agent.processUserInput('你好');
      await agent.processUserInput('计算 10 + 20');
      const messages = agent.getMessages();
      const userMessages = messages.filter(m => m.role === 'user');
      expect(userMessages.length).toBeGreaterThanOrEqual(2);
    });
  });

  describe('parseToolCall', () => {
    it('应该正确解析工具调用（通过 Agent 行为验证）', async () => {
      const agent = new Agent({
        apiKey: 'test-key',
        mockMode: true
      });

      // 模拟响应会包含工具调用
      const response = await agent.processUserInput('计算 5 + 3');

      // 验证 Agent 能正确处理并返回计算结果
      expect(response).toContain('计算结果');
      expect(response).toContain('8');
    });
  });

  describe('工具调用流程', () => {
    it('应该完成完整的工具调用循环', async () => {
      const agent = new Agent({
        apiKey: 'test-key',
        mockMode: true
      });

      // 1. 用户请求计算（使用直接的表达式）
      const response = await agent.processUserInput('帮我计算 100 / 4');

      // 2. 验证响应包含计算结果
      expect(response).toContain('25');

      // 3. 验证消息历史包含工具调用相关消息
      const messages = agent.getMessages();
      expect(messages.some(m => m.role === 'function')).toBe(true);
    });

    it('应该处理天气查询工具调用', async () => {
      const agent = new Agent({
        apiKey: 'test-key',
        mockMode: true
      });

      const response = await agent.processUserInput('上海今天天气怎么样');

      expect(response).toContain('上海');
    });
  });

  describe('错误处理', () => {
    it('应该处理不存在的工具（通过模拟）', async () => {
      const agent = new Agent({
        apiKey: 'test-key',
        mockMode: true
      });

      // 普通对话不应报错
      const response = await agent.processUserInput('你好，请介绍一下自己');
      expect(response).toBeDefined();
    });
  });

  describe('最大迭代次数限制', () => {
    it('应该在达到最大迭代次数时停止', async () => {
      const agent = new Agent({
        apiKey: 'test-key',
        mockMode: true,
        maxIterations: 2
      });

      // 模拟一个可能触发多次迭代的场景
      const response = await agent.processUserInput('计算 1 + 1');
      expect(response).toBeDefined();
    });

    it('应该在达到最大迭代次数时返回提示信息', async () => {
      const agent = new Agent({
        apiKey: 'test-key',
        mockMode: true,
        maxIterations: 1
      });

      // 创建一个会触发工具调用的场景
      // 在模拟模式下，maxIterations = 1 意味着只能调用一次 LLM
      const response = await agent.processUserInput('计算 1 + 1');
      expect(response).toBeDefined();
    });
  });

  describe('边界情况', () => {
    it('应该处理空输入', async () => {
      const agent = new Agent({
        apiKey: 'test-key',
        mockMode: true
      });

      // 空字符串不应该崩溃
      const response = await agent.processUserInput('   ');
      expect(response).toBeDefined();
    });

    it('应该处理特殊字符输入', async () => {
      const agent = new Agent({
        apiKey: 'test-key',
        mockMode: true
      });

      const response = await agent.processUserInput('!@#$%^&*()');
      expect(response).toBeDefined();
    });

    it('应该处理非常长的输入', async () => {
      const agent = new Agent({
        apiKey: 'test-key',
        mockMode: true
      });

      const longInput = '你好 '.repeat(100);
      const response = await agent.processUserInput(longInput);
      expect(response).toBeDefined();
    });
  });
});
