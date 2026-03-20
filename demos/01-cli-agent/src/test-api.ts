import { config } from 'dotenv';
import { createClient, LLMProvider } from './providers/index.js';

config();

interface TestResult {
  success: boolean;
  message: string;
  details?: any;
}

// 默认模型配置
const DEFAULT_MODELS: Record<LLMProvider, string> = {
  [LLMProvider.ZHIPUAI]: 'glm-5',
  [LLMProvider.MINIMAX]: 'M2-her',
  [LLMProvider.KIMI]: 'moonshot-v1-8k'
};

/**
 * 错误码说明映射（智谱 AI）
 */
const ZHIPU_ERROR_CODES: Record<string, string> = {
  '1101': '未授权，API Key 无效',
  '1102': '请求频率超限',
  '1103': '模型不存在',
  '1113': '余额不足或无可用资源包',
  '1200': '服务器内部错误',
  '1201': '请求超时',
  '1301': '参数错误'
};

/**
 * 脱敏显示 API Key
 */
function maskApiKey(apiKey: string): string {
  if (apiKey.length < 10) {
    return '***TOO_SHORT***';
  }
  return `${apiKey.slice(0, 6)}...${apiKey.slice(-4)}`;
}

/**
 * 获取 API Key（支持多种配置方式）
 */
function getApiKey(provider: LLMProvider): string {
  switch (provider) {
    case LLMProvider.ZHIPUAI:
      return process.env.ZHIPUAI_API_KEY || process.env.LLM_API_KEY || '';
    case LLMProvider.MINIMAX:
      return process.env.MINIMAX_API_KEY || process.env.LLM_API_KEY || '';
    case LLMProvider.KIMI:
      return process.env.KIMI_API_KEY || process.env.LLM_API_KEY || '';
    default:
      return process.env.LLM_API_KEY || '';
  }
}

/**
 * 获取模型名称
 */
function getModel(provider: LLMProvider): string {
  switch (provider) {
    case LLMProvider.ZHIPUAI:
      return process.env.ZHIPUAI_MODEL || DEFAULT_MODELS[provider];
    case LLMProvider.MINIMAX:
      return process.env.MINIMAX_MODEL || DEFAULT_MODELS[provider];
    case LLMProvider.KIMI:
      return process.env.KIMI_MODEL || DEFAULT_MODELS[provider];
    default:
      return DEFAULT_MODELS[provider];
  }
}

/**
 * 获取 Base URL
 */
function getBaseURL(provider: LLMProvider): string | undefined {
  switch (provider) {
    case LLMProvider.ZHIPUAI:
      return process.env.ZHIPUAI_BASE_URL || 'https://open.bigmodel.cn/api/coding/paas/v4';
    case LLMProvider.MINIMAX:
      return process.env.MINIMAX_BASE_URL;
    case LLMProvider.KIMI:
      return process.env.KIMI_BASE_URL;
    default:
      return undefined;
  }
}

/**
 * 测试 LLM API 可用性
 */
export async function testLLMAPI(provider: LLMProvider): Promise<TestResult> {
  const apiKey = getApiKey(provider);
  const model = getModel(provider);
  const baseURL = getBaseURL(provider);

  // 检查环境变量
  if (!apiKey) {
    return {
      success: false,
      message: `未找到 ${provider} 的 API Key`,
      details: {
        provider,
        hint: `请在 .env 文件中设置 ${provider.toUpperCase()}_API_KEY 或 LLM_API_KEY`
      }
    };
  }

  console.log(`🔌 提供商: ${provider}`);
  console.log(`🔑 API Key: ${maskApiKey(apiKey)}`);
  console.log(`🤖 模型: ${model}`);
  if (baseURL) {
    console.log(`🔗 端点: ${baseURL}`);
  }

  try {
    console.log('📡 正在发送测试请求...');

    // 使用统一的适配器接口
    const client = createClient(provider, apiKey, baseURL);
    const response = await client.chat({
      model,
      messages: [{ role: 'user', content: '你好' }],
      stream: false
    });

    // 验证响应
    if (!response.content) {
      return {
        success: false,
        message: 'API 返回空响应',
        details: { provider, response }
      };
    }

    return {
      success: true,
      message: 'API 调用成功',
      details: {
        provider,
        model,
        response: response.content,
        usage: response.usage
      }
    };
  } catch (error: any) {
    // 解析错误信息
    const errorCode = error?.error?.code || error?.code || 'UNKNOWN';
    const errorMessage = error?.error?.message || error?.message || '未知错误';

    return {
      success: false,
      message: `API 调用失败 [${errorCode}]`,
      details: {
        provider,
        errorCode,
        errorMessage,
        explanation: ZHIPU_ERROR_CODES[errorCode] || '未知错误码',
        rawError: {
          name: error.name,
          message: error.message,
          stack: error.stack?.split('\n').slice(0, 3).join('\n')
        }
      }
    };
  }
}

/**
 * 打印分隔线
 */
function printSeparator(char: string = '━', length: number = 50) {
  console.log(char.repeat(length));
}

/**
 * 解析命令行参数获取提供商
 */
function getProviderFromArgs(): LLMProvider {
  const providerArg = process.argv.find(arg => arg.startsWith('--provider='));
  if (providerArg) {
    const provider = providerArg.split('=')[1] as LLMProvider;
    if (Object.values(LLMProvider).includes(provider)) {
      return provider;
    }
    console.warn(`⚠️  未知的提供商: ${provider}，将使用默认值`);
  }

  // 从环境变量读取
  const envProvider = process.env.LLM_PROVIDER as LLMProvider;
  if (envProvider && Object.values(LLMProvider).includes(envProvider)) {
    return envProvider;
  }

  // 默认使用智谱
  return LLMProvider.ZHIPUAI;
}

/**
 * 主函数
 */
async function main() {
  const provider = getProviderFromArgs();

  console.clear();
  console.log(`🧪 LLM API 可用性测试 (${provider})\n`);
  printSeparator('━', 50);
  console.log();

  const result = await testLLMAPI(provider);

  console.log();

  if (result.success) {
    console.log('✅ 测试成功！\n');
    console.log('📋 详细信息:');
    console.log(`   提供商: ${result.details.provider}`);
    console.log(`   模型: ${result.details.model}`);
    if (result.details.usage) {
      console.log(`\n📊 Token 使用:`);
      console.log(`   输入: ${result.details.usage.prompt_tokens || 'N/A'}`);
      console.log(`   输出: ${result.details.usage.completion_tokens || 'N/A'}`);
      console.log(`   总计: ${result.details.usage.total_tokens || 'N/A'}`);
    }
    console.log(`\n💬 AI 响应:`);
    console.log(`   ${result.details.response}`);
  } else {
    console.log('❌ 测试失败！\n');
    console.log(`🔍 错误: ${result.message}`);
    if (result.details) {
      if (result.details.explanation) {
        console.log(`📖 说明: ${result.details.explanation}`);
      }
      if (result.details.hint) {
        console.log(`💡 提示: ${result.details.hint}`);
      }
      if (result.details.errorCode) {
        console.log(`\n📝 错误详情:`);
        console.log(`   错误码: ${result.details.errorCode}`);
        console.log(`   错误信息: ${result.details.errorMessage}`);
      }
      if (result.details.rawError) {
        console.log(`\n🐛 原始错误:`);
        console.log(`   ${result.details.rawError.name}: ${result.details.rawError.message}`);
      }
    }
  }

  console.log();
  printSeparator('━', 50);
  console.log();

  // 根据测试结果提供建议
  if (!result.success) {
    const errorCode = result.details?.errorCode;
    if (errorCode === '1113') {
      console.log('🔧 解决建议:');
      console.log('   1. 登录对应平台的控制台检查账户余额');
      console.log('   2. 购买或充值资源包');
      console.log('   3. 确认使用的是付费 API Key（非免费额度）');
    } else if (errorCode === '1101') {
      console.log('🔧 解决建议:');
      console.log('   1. 检查 .env 文件中的 API Key 是否正确复制');
      console.log('   2. 确认没有多余的空格或换行符');
      console.log('   3. 重新生成 API Key 并尝试');
    } else if (errorCode === '1102') {
      console.log('🔧 解决建议:');
      console.log('   1. 降低请求频率');
      console.log('   2. 考虑升级套餐以获得更高的 QPS');
    }
    console.log();
  }
}

main().catch(error => {
  console.error('💥 程序异常:', error);
  process.exit(1);
});
