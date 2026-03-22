import { test, expect } from '@playwright/test';

/**
 * 聊天功能 E2E 测试
 */
test.describe('聊天功能', () => {
  test.beforeEach(async ({ page }) => {
    // 每个测试生成唯一的用户名（使用随机数避免并行冲突）
    const randomSuffix = Math.floor(Math.random() * 1000000);
    const testUser = {
      username: `chat_test_${randomSuffix}`,
      password: 'testpass123'
    };

    // 注册并登录
    await page.goto('/auth');
    await page.click('text=立即注册');
    await page.fill('input[placeholder="请输入用户名"]', testUser.username);
    await page.fill('input[placeholder="请输入密码（至少6位）"]', testUser.password);
    await page.fill('input[placeholder="请再次输入密码"]', testUser.password);
    await page.click('button:has-text("注册")');

    // 等待跳转到首页（聊天界面），增加超时时间
    await page.waitForURL('/', { timeout: 20000 });
  });

  test('应该显示聊天界面', async ({ page }) => {
    // 应该看到输入框（使用 textarea）
    await expect(page.locator('textarea[placeholder*="输入你的消息"]')).toBeVisible();

    // 应该看到发送按钮
    await expect(page.locator('button:has-text("发送")')).toBeVisible();
  });

  test('应该成功发送消息', async ({ page }) => {
    const testMessage = '你好，这是一个测试消息';

    // 输入消息
    await page.fill('textarea[placeholder*="输入你的消息"]', testMessage);

    // 发送消息
    await page.click('button:has-text("发送")');

    // 应该看到用户消息
    await expect(page.locator(`.message-user`)).toContainText(testMessage, { timeout: 5000 });
  });

  test('应该接收 AI 的流式响应', async ({ page }) => {
    const testMessage = '你好';

    // 发送消息
    await page.fill('textarea[placeholder*="输入你的消息"]', testMessage);
    await page.click('button:has-text("发送")');

    // 等待 AI 响应（流式输出）
    await page.waitForSelector('.message-assistant', { timeout: 10000 });

    // 验证响应不为空
    const assistantMessage = await page.locator('.message-assistant .message-text').first();
    const text = await assistantMessage.textContent();
    expect(text?.trim()).not.toBe('');
  });

  test('应该支持多轮对话', async ({ page }) => {
    // 第一轮
    await page.fill('textarea[placeholder*="输入你的消息"]', '第一条消息');
    await page.click('button:has-text("发送")');
    await page.waitForSelector('.message-assistant', { timeout: 10000 });

    // 第二轮
    await page.fill('textarea[placeholder*="输入你的消息"]', '第二条消息');
    await page.click('button:has-text("发送")');
    await page.waitForSelector('.message-assistant', { timeout: 10000 });

    // 应该看到多轮对话记录
    const userMessages = await page.locator('.message-user').count();
    const assistantMessages = await page.locator('.message-assistant').count();

    expect(userMessages).toBeGreaterThanOrEqual(2);
    expect(assistantMessages).toBeGreaterThanOrEqual(2);
  });

  test('应该正确区分用户消息和 AI 消息', async ({ page }) => {
    const testMessage = '测试消息';

    await page.fill('textarea[placeholder*="输入你的消息"]', testMessage);
    await page.click('button:has-text("发送")');
    await page.waitForSelector('.message-assistant', { timeout: 10000 });

    // 用户消息应该有特定样式
    const userMsg = page.locator('.message-user');
    await expect(userMsg).toBeVisible();
    await expect(userMsg).toContainText(testMessage);

    // AI 消息应该有不同的样式
    const assistantMsg = page.locator('.message-assistant');
    await expect(assistantMsg).toBeVisible();
  });

  test('输入框应该在发送后清空', async ({ page }) => {
    const testMessage = '测试消息';

    await page.fill('textarea[placeholder*="输入你的消息"]', testMessage);
    await page.click('button:has-text("发送")');

    // 等待消息发送
    await page.waitForTimeout(500);

    // 输入框应该被清空
    const inputValue = await page.inputValue('textarea[placeholder*="输入你的消息"]');
    expect(inputValue).toBe('');
  });

  test('应该禁用空消息发送', async ({ page }) => {
    // 尝试发送空消息
    const sendButton = page.locator('button:has-text("发送")');

    // 发送按钮应该被禁用（输入为空时）
    await page.fill('textarea[placeholder*="输入你的消息"]', '');
    const isDisabled = await sendButton.isDisabled();

    if (!isDisabled) {
      // 如果不禁用，点击后应该没有效果
      await sendButton.click();
      await page.waitForTimeout(500);
      const messageCount = await page.locator('.message-user, .message-assistant').count();
      expect(messageCount).toBe(0);
    }
  });

  test('应该正确处理 Ctrl+Enter 发送', async ({ page }) => {
    const testMessage = 'Ctrl+Enter 测试';

    await page.fill('textarea[placeholder*="输入你的消息"]', testMessage);

    // 按 Ctrl+Enter 发送
    await page.press('textarea[placeholder*="输入你的消息"]', 'Control+Enter');

    // 应该发送消息
    await expect(page.locator('.message-user')).toContainText(testMessage, { timeout: 5000 });
  });
});
