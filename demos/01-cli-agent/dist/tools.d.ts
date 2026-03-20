import type { Tool } from './types.js';
/**
 * 工具 1: 计算器
 * 执行数学计算，支持加减乘除和括号
 */
export declare const calculatorTool: Tool;
/**
 * 工具 2: 天气查询（模拟）
 * 查询指定城市的天气信息
 */
export declare const weatherTool: Tool;
/**
 * 工具列表
 */
export declare const tools: Tool[];
/**
 * 获取工具列表的描述文本
 */
export declare function getToolDescriptions(): string;
/**
 * 根据名称查找工具
 */
export declare function findTool(name: string): Tool | undefined;
//# sourceMappingURL=tools.d.ts.map