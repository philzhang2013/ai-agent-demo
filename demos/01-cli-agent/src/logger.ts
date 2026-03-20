/**
 * 简单的日志工具
 * 支持不同级别的日志输出和格式化
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  SUCCESS = 2,
  WARNING = 3,
  ERROR = 4
}

const LOG_COLORS = {
  [LogLevel.DEBUG]: '\x1b[90m',    // 灰色
  [LogLevel.INFO]: '\x1b[36m',     // 青色
  [LogLevel.SUCCESS]: '\x1b[32m',  // 绿色
  [LogLevel.WARNING]: '\x1b[33m',  // 黄色
  [LogLevel.ERROR]: '\x1b[31m',    // 红色
  RESET: '\x1b[0m'
};

const LOG_ICONS = {
  [LogLevel.DEBUG]: '🔍',
  [LogLevel.INFO]: 'ℹ️ ',
  [LogLevel.SUCCESS]: '✅',
  [LogLevel.WARNING]: '⚠️ ',
  [LogLevel.ERROR]: '❌'
};

let currentLogLevel = LogLevel.DEBUG;
let showTimestamp = true;
let showIcons = true;

/**
 * 设置日志级别
 */
export function setLogLevel(level: LogLevel): void {
  currentLogLevel = level;
}

/**
 * 启用/禁用时间戳
 */
export function setShowTimestamp(enabled: boolean): void {
  showTimestamp = enabled;
}

/**
 * 启用/禁用图标
 */
export function setShowIcons(enabled: boolean): void {
  showIcons = enabled;
}

/**
 * 获取时间戳
 */
function getTimestamp(): string {
  if (!showTimestamp) return '';
  const now = new Date();
  const hh = String(now.getHours()).padStart(2, '0');
  const mm = String(now.getMinutes()).padStart(2, '0');
  const ss = String(now.getSeconds()).padStart(2, '0');
  const ms = String(now.getMilliseconds()).padStart(3, '0');
  return `[${hh}:${mm}:${ss}.${ms}] `;
}

/**
 * 格式化输出
 */
function format(level: LogLevel, category: string, message: string): void {
  if (level < currentLogLevel) return;

  const color = LOG_COLORS[level];
  const reset = LOG_COLORS.RESET;
  const icon = showIcons ? LOG_ICONS[level] + ' ' : '';
  const timestamp = getTimestamp();

  // 输出到 stderr（不影响 stdout 的交互）
  console.error(`${color}${timestamp}${icon}[${category}]${reset} ${message}`);
}

/**
 * 日志函数
 */
export const logger = {
  debug: (category: string, message: string) => format(LogLevel.DEBUG, category, message),
  info: (category: string, message: string) => format(LogLevel.INFO, category, message),
  success: (category: string, message: string) => format(LogLevel.SUCCESS, category, message),
  warning: (category: string, message: string) => format(LogLevel.WARNING, category, message),
  error: (category: string, message: string) => format(LogLevel.ERROR, category, message)
};

/**
 * 格式化 JSON 为易读字符串
 */
export function formatJSON(obj: any, indent: number = 2): string {
  return JSON.stringify(obj, null, indent);
}

/**
 * 格式化消息列表
 */
export function formatMessages(messages: any[]): string {
  return messages.map((msg, idx) => {
    const role = msg.role?.padEnd(10);
    const content = msg.content?.substring(0, 100) + (msg.content?.length > 100 ? '...' : '');
    return `  [${idx + 1}] ${role} ${content}`;
  }).join('\n');
}

/**
 * 创建分隔线
 */
export function separator(char: string = '─', length: number = 60): string {
  return char.repeat(length);
}
