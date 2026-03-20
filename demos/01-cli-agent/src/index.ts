import * as readline from 'readline';
import { config } from 'dotenv';
import { Agent } from './agent.js';
import { LLMProvider } from './providers/index.js';
import { LogLevel, setLogLevel } from './logger.js';

// 加载环境变量
config();

// 配置日志级别（默认 DEBUG，方便观察运行过程）
const logLevelStr = process.env.LOG_LEVEL?.toUpperCase() || 'DEBUG';
const logLevelMap: Record<string, LogLevel> = {
  'DEBUG': LogLevel.DEBUG,
  'INFO': LogLevel.INFO,
  'SUCCESS': LogLevel.SUCCESS,
  'WARNING': LogLevel.WARNING,
  'ERROR': LogLevel.ERROR
};
setLogLevel(logLevelMap[logLevelStr] || LogLevel.DEBUG);

// ========== 配置加载 ==========

interface Config {
  provider: LLMProvider;
  apiKey: string;
  baseURL?: string;
  model?: string;
  mockMode: boolean;
}

/**
 * 从环境变量加载配置
 * 支持新旧两种配置方式
 */
function loadConfig(): Config {
  // 获取提供商（默认智谱，向后兼容）
  const provider = (process.env.LLM_PROVIDER as LLMProvider) || LLMProvider.ZHIPUAI;
  const mockMode = process.env.MOCK_LLM === 'true';

  // 获取 API Key（支持多种配置方式）
  let apiKey: string;
  let baseURL: string | undefined;
  switch (provider) {
    case LLMProvider.ZHIPUAI:
      apiKey = process.env.ZHIPUAI_API_KEY || process.env.LLM_API_KEY || '';
      // 智谱 CodePlan 默认使用专用端点
      baseURL = process.env.ZHIPUAI_BASE_URL || 'https://open.bigmodel.cn/api/coding/paas/v4';
      break;
    case LLMProvider.MINIMAX:
      apiKey = process.env.MINIMAX_API_KEY || process.env.LLM_API_KEY || '';
      baseURL = process.env.MINIMAX_BASE_URL;
      break;
    case LLMProvider.KIMI:
      apiKey = process.env.KIMI_API_KEY || process.env.LLM_API_KEY || '';
      baseURL = process.env.KIMI_BASE_URL;
      break;
    default:
      apiKey = process.env.LLM_API_KEY || '';
  }

  // 获取模型配置（可选）
  let model: string | undefined;
  switch (provider) {
    case LLMProvider.ZHIPUAI:
      model = process.env.ZHIPUAI_MODEL;
      break;
    case LLMProvider.MINIMAX:
      model = process.env.MINIMAX_MODEL;
      break;
    case LLMProvider.KIMI:
      model = process.env.KIMI_MODEL;
      break;
  }

  return { provider, apiKey, baseURL, model, mockMode };
}

// ========== 命令行界面 ==========

function createCLI(): readline.Interface {
  return readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
}

function question(rl: readline.Interface, prompt: string): Promise<string> {
  return new Promise((resolve) => {
    rl.question(prompt, (answer) => {
      resolve(answer);
    });
  });
}

async function main() {
  const config = loadConfig();

  // 验证配置
  if (!config.apiKey && !config.mockMode) {
    console.error('❌ 错误: 未检测到 API Key');
    console.error(`\n当前提供商: ${config.provider}`);
    console.error('\n请设置以下环境变量之一：');
    switch (config.provider) {
      case LLMProvider.ZHIPUAI:
        console.error('  - ZHIPUAI_API_KEY（推荐）');
        console.error('  - LLM_API_KEY（通用）');
        break;
      case LLMProvider.MINIMAX:
        console.error('  - MINIMAX_API_KEY（推荐）');
        console.error('  - LLM_API_KEY（通用）');
        break;
      case LLMProvider.KIMI:
        console.error('  - KIMI_API_KEY（推荐）');
        console.error('  - LLM_API_KEY（通用）');
        break;
    }
    console.error('\n或在 .env 文件中设置 MOCK_LLM=true 使用模拟模式');
    process.exit(1);
  }

  console.log('🤖 命令行 AI Agent Demo');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  if (config.mockMode) {
    console.log('🧪 模拟模式已启用（不会调用真实 API）');
  } else {
    console.log(`🔌 提供商: ${config.provider}`);
  }
  console.log('输入 "quit" 或 "exit" 退出\n');

  const agent = new Agent({
    provider: config.provider,
    apiKey: config.apiKey,
    baseURL: config.baseURL,
    model: config.model,
    mockMode: config.mockMode
  });

  const rl = createCLI();

  try {
    while (true) {
      const input = await question(rl, '👤 你: ');

      if (input.toLowerCase() === 'quit' || input.toLowerCase() === 'exit') {
        console.log('\n👋 再见！');
        break;
      }

      if (!input.trim()) {
        continue;
      }

      const response = await agent.processUserInput(input);
      console.log(`\n🤖 助手: ${response}\n`);
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    }
  } catch (error) {
    console.error('发生错误:', error);
  } finally {
    rl.close();
  }
}

main();
