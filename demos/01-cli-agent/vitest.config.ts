import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    // 测试环境
    environment: 'node',

    // 全局配置
    globals: true,

    // 覆盖率配置
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      // 覆盖率阈值（针对核心业务代码）
      // 注意：真实 API 调用代码在模拟模式下不执行，因此阈值设为 70%
      lines: 70,
      functions: 95,
      branches: 75,
      statements: 70,
      // 排除的文件
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.test.ts',
        '**/*.spec.ts',
        // 排除不需要测试的文件
        '**/index.ts',           // CLI 入口文件（交互式代码）
        '**/types.ts',           // 类型定义（不需要测试）
        'vitest.config.ts',      // 配置文件
      ],
      // 只包含 src 目录下的文件进行覆盖率统计
      include: ['src/**/*.ts'],
    },

    // 测试文件匹配模式
    include: ['tests/**/*.test.ts'],

    // 并行执行
    threads: true,

    // 显示详细信息
    reporters: ['verbose'],
  },
});
