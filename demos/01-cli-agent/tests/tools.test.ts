import { describe, it, expect } from 'vitest';
import { calculatorTool, weatherTool, tools, getToolDescriptions, findTool } from '../src/tools.js';

describe('工具函数测试', () => {
  describe('calculatorTool', () => {
    it('应该正确执行加法运算', async () => {
      const result = await calculatorTool.execute({ expression: '18 + 25' });
      expect(result).toBe('计算结果: 18 + 25 = 43');
    });

    it('应该正确执行减法运算', async () => {
      const result = await calculatorTool.execute({ expression: '50 - 15' });
      expect(result).toBe('计算结果: 50 - 15 = 35');
    });

    it('应该正确执行乘法运算', async () => {
      const result = await calculatorTool.execute({ expression: '6 * 7' });
      expect(result).toBe('计算结果: 6 * 7 = 42');
    });

    it('应该正确执行除法运算', async () => {
      const result = await calculatorTool.execute({ expression: '100 / 4' });
      expect(result).toBe('计算结果: 100 / 4 = 25');
    });

    it('应该正确处理括号表达式', async () => {
      const result = await calculatorTool.execute({ expression: '(10 * 5) / 2' });
      expect(result).toBe('计算结果: (10 * 5) / 2 = 25');
    });

    it('应该处理包含空格的表达式', async () => {
      const result = await calculatorTool.execute({ expression: ' 2 + 3 ' });
      expect(result).toBe('计算结果: 2 + 3 = 5');
    });

    it('应该处理无效表达式并返回错误', async () => {
      const result = await calculatorTool.execute({ expression: 'invalid' });
      expect(result).toContain('计算错误');
    });
  });

  describe('weatherTool', () => {
    it('应该返回北京的天气信息', async () => {
      const result = await weatherTool.execute({ city: '北京' });
      expect(result).toContain('北京');
      expect(result).toContain('晴天');
      expect(result).toContain('18');
      expect(result).toContain('75');
    });

    it('应该返回上海的天气信息', async () => {
      const result = await weatherTool.execute({ city: '上海' });
      expect(result).toContain('上海');
      expect(result).toContain('多云');
      expect(result).toContain('22');
    });

    it('应该返回深圳的天气信息', async () => {
      const result = await weatherTool.execute({ city: '深圳' });
      expect(result).toContain('深圳');
      expect(result).toContain('阴天');
      expect(result).toContain('25');
    });

    it('应该返回广州的天气信息', async () => {
      const result = await weatherTool.execute({ city: '广州' });
      expect(result).toContain('广州');
      expect(result).toContain('小雨');
      expect(result).toContain('24');
    });

    it('应该对未知城市返回默认值', async () => {
      const result = await weatherTool.execute({ city: '杭州' });
      expect(result).toContain('杭州');
      expect(result).toContain('未知');
      expect(result).toContain('--');
    });
  });

  describe('工具列表', () => {
    it('应该包含两个工具', () => {
      expect(tools).toHaveLength(2);
    });

    it('应该包含 calculator 工具', () => {
      expect(tools.find(t => t.name === 'calculator')).toBeDefined();
    });

    it('应该包含 get_weather 工具', () => {
      expect(tools.find(t => t.name === 'get_weather')).toBeDefined();
    });
  });

  describe('getToolDescriptions', () => {
    it('应该返回工具描述列表', () => {
      const descriptions = getToolDescriptions();
      expect(descriptions).toContain('- calculator: 执行数学计算');
      expect(descriptions).toContain('- get_weather: 查询指定城市的天气信息');
    });
  });

  describe('findTool', () => {
    it('应该找到 calculator 工具', () => {
      const tool = findTool('calculator');
      expect(tool).toBeDefined();
      expect(tool?.name).toBe('calculator');
    });

    it('应该找到 get_weather 工具', () => {
      const tool = findTool('get_weather');
      expect(tool).toBeDefined();
      expect(tool?.name).toBe('get_weather');
    });

    it('对不存在的工具应该返回 undefined', () => {
      const tool = findTool('nonexistent');
      expect(tool).toBeUndefined();
    });
  });
});
