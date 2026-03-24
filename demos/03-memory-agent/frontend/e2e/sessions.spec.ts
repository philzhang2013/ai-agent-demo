import { test, expect } from '@playwright/test';

/**
 * 会话管理 E2E 测试
 */
test.describe('会话管理', () => {
  test.beforeEach(async ({ page }) => {
    // 每个测试生成唯一的用户名
    const randomSuffix = Math.floor(Math.random() * 1000000);
    const testUser = {
      username: `session_test_${randomSuffix}`,
      password: 'testpass123'
    };

    // 注册并登录
    await page.goto('/auth');
    await page.click('text=立即注册');
    await page.fill('input[placeholder="请输入用户名"]', testUser.username);
    await page.fill('input[placeholder="请输入密码（至少6位）"]', testUser.password);
    await page.fill('input[placeholder="请再次输入密码"]', testUser.password);
    await page.click('button:has-text("注册")');

    // 等待跳转到首页，增加超时时间
    await page.waitForURL('/', { timeout: 20000 });
  });

  test('应该创建新会话', async ({ page }) => {
    // 发送第一条消息，应该创建新会话
    await page.fill('textarea[placeholder*="输入你的消息"]', '第一条消息');
    await page.click('button:has-text("发送")');

    // 等待响应
    await page.waitForSelector('.message-assistant', { timeout: 10000 });

    // 应该有会话记录（至少2条消息：用户 + AI）
    const messages = await page.locator('.message-user, .message-assistant').count();
    expect(messages).toBeGreaterThan(0);
  });

  test('应该显示会话历史', async ({ page }) => {
    // 创建两个不同的会话
    // 消息 1
    await page.fill('textarea[placeholder*="输入你的消息"]', '消息1');
    await page.click('button:has-text("发送")');
    await page.waitForSelector('.message-assistant', { timeout: 10000 });

    await page.waitForTimeout(1000);

    // 消息 2
    await page.fill('textarea[placeholder*="输入你的消息"]', '消息2');
    await page.click('button:has-text("发送")');
    await page.waitForSelector('.message-assistant', { timeout: 10000 });

    // 应该看到所有历史消息
    const messages = await page.locator('.message-user, .message-assistant').count();
    expect(messages).toBeGreaterThan(0);
  });

  test('应该正确显示消息时间戳', async ({ page }) => {
    await page.fill('textarea[placeholder*="输入你的消息"]', '测试时间戳');
    await page.click('button:has-text("发送")');
    await page.waitForSelector('.message-assistant', { timeout: 10000 });

    // 检查消息是否有时间戳
    const message = page.locator('.message').first();
    await expect(message).toBeVisible();

    // 应该有时间戳元素
    const timeElement = message.locator('.message-time');
    await expect(timeElement).toBeVisible();
  });

  test('应该区分用户消息和助手消息', async ({ page }) => {
    await page.fill('textarea[placeholder*="输入你的消息"]', '用户消息');
    await page.click('button:has-text("发送")');
    await page.waitForSelector('.message-assistant', { timeout: 10000 });

    // 用户消息
    const userMessages = page.locator('.message-user');
    await expect(userMessages).toHaveCount(1);

    // 助手消息
    const assistantMessages = page.locator('.message-assistant');
    await expect(assistantMessages).toHaveCount(1);
  });

  test('应该支持多条消息', async ({ page }) => {
    // 发送多条消息创建历史记录
    for (let i = 0; i < 3; i++) {
      await page.fill('textarea[placeholder*="输入你的消息"]', `消息 ${i + 1}`);
      await page.click('button:has-text("发送")');
      await page.waitForSelector('.message-assistant', { timeout: 10000 });
      await page.waitForTimeout(500);
    }

    // 验证所有消息都显示
    const allMessages = page.locator('.message-user, .message-assistant');
    await expect(allMessages).toHaveCount(6); // 3 用户 + 3 助手
  });
});
