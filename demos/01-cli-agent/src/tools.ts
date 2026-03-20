import { log } from 'console';
import type { Tool } from './types.js';
import { logger } from './logger.js';

// ========== 工具定义 ==========

/**
 * 工具 1: 计算器
 * 执行数学计算，支持加减乘除和括号
 */
export const calculatorTool: Tool = {
  name: 'calculator',
  description: '执行数学计算，支持加减乘除和括号',
  parameters: {
    type: 'object',
    properties: {
      expression: {
        type: 'string',
        description: '要计算的数学表达式，例如 "18 + 25" 或 "(10 * 5) / 2"'
      }
    },
    required: ['expression']
  },
  execute: (args) => {
    try {
      // 去除表达式前后空格
      const expression = args.expression.trim();
      logger.info("TOOL", `执行计算器工具: ${expression}`);
      // 安全地计算表达式
      const result = Function('"use strict"; return (' + expression + ')')();
      return `计算结果: ${expression} = ${result}`;
    } catch (error) {
      return `计算错误: ${error}`;
    }
  }
};

/**
 * 模拟天气数据
 */
const weatherData: Record<string, { condition: string; temperature: number; aqi: number }> = {
  '北京': { condition: '晴天', temperature: 18, aqi: 75 },
  '上海': { condition: '多云', temperature: 22, aqi: 60 },
  '深圳': { condition: '阴天', temperature: 25, aqi: 45 },
  '广州': { condition: '小雨', temperature: 24, aqi: 55 },
};

/**
 * 工具 2: 天气查询（模拟）
 * 查询指定城市的天气信息
 */
export const weatherTool: Tool = {
  name: 'get_weather',
  description: '查询指定城市的天气信息',
  parameters: {
    type: 'object',
    properties: {
      city: {
        type: 'string',
        description: '城市名称，例如 "北京"、"上海"'
      }
    },
    required: ['city']
  },
  execute: (args) => {
    const data = weatherData[args.city] || { condition: '未知', temperature: '--', aqi: '--' };
    return `${args.city}今天${data.condition}，温度 ${data.temperature}°C，空气质量 ${data.aqi}`;
  }
};

/**
 * 工具列表
 */
export const tools: Tool[] = [calculatorTool, weatherTool];

/**
 * 获取工具列表的描述文本
 */
export function getToolDescriptions(): string {
  return tools.map(tool => `- ${tool.name}: ${tool.description}`).join('\n');
}

/**
 * 根据名称查找工具
 */
export function findTool(name: string): Tool | undefined {
  return tools.find(t => t.name === name);
}
