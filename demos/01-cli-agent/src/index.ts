import * as readline from 'readline';
import { config } from 'dotenv';
import { Agent } from './agent.js';

// 加载环境变量
config();

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
  const apiKey = process.env.ZHIPUAI_API_KEY;
  const mockMode = process.env.MOCK_LLM === 'true';

  if (!apiKey && !mockMode) {
    console.error('❌ 错误: 请在 .env 文件中设置 ZHIPUAI_API_KEY，或设置 MOCK_LLM=true 使用模拟模式');
    process.exit(1);
  }

  console.log('🤖 命令行 AI Agent Demo');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  if (mockMode) {
    console.log('🧪 模拟模式已启用（不会调用真实 API）');
  }
  console.log('输入 "quit" 或 "exit" 退出\n');

  const agent = new Agent({
    apiKey: apiKey || '',
    mockMode
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
