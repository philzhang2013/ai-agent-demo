import { test, expect } from '@playwright/test';

/**
 * 认证流程 E2E 测试
 */
test.describe('用户认证流程', () => {
  test.beforeEach(async ({ page }) => {
    // 清除 localStorage
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.clear();
    });
  });

  test('应该显示登录/注册页面', async ({ page }) => {
    await page.goto('/');

    // 应该重定向到认证页面
    await page.waitForURL('/auth');
    await expect(page).toHaveTitle(/Web Agent Demo/);

    // 应该看到登录表单
    await expect(page.locator('h2')).toContainText('登录');
  });

  test('应该成功注册新用户', async ({ page }) => {
    // 每个测试生成唯一的用户名
    const randomSuffix = Math.floor(Math.random() * 1000000);
    const testUser = {
      username: `testuser_${randomSuffix}`,
      password: 'testpass123'
    };

    await page.goto('/auth');

    // 点击注册链接
    await page.click('text=立即注册');

    // 填写注册表单
    await page.fill('input[placeholder="请输入用户名"]', testUser.username);
    await page.fill('input[placeholder="请输入密码（至少6位）"]', testUser.password);

    // 填写确认密码
    await page.fill('input[placeholder="请再次输入密码"]', testUser.password);

    // 提交注册
    await page.click('button:has-text("注册")');

    // 等待跳转到聊天页面
    await page.waitForURL('/', { timeout: 20000 });

    // 验证注册成功 - 应该在首页
    await expect(page).toHaveURL('/');
  });

  test('应该成功登录已注册用户', async ({ page }) => {
    // 每个测试生成唯一的用户名
    const randomSuffix = Math.floor(Math.random() * 1000000);
    const testUser = {
      username: `testuser_${randomSuffix}`,
      password: 'testpass123'
    };

    // 首先注册用户
    await page.goto('/auth');
    await page.click('text=立即注册');
    await page.fill('input[placeholder="请输入用户名"]', testUser.username);
    await page.fill('input[placeholder="请输入密码（至少6位）"]', testUser.password);
    await page.fill('input[placeholder="请再次输入密码"]', testUser.password);
    await page.click('button:has-text("注册")');
    await page.waitForURL('/', { timeout: 20000 });

    // 退出登录（使用圆形按钮的选择器）
    await page.click('.el-header .el-button--circle');
    await page.waitForURL('/auth', { timeout: 5000 });

    // 重新登录
    await page.fill('input[placeholder="请输入用户名"]', testUser.username);
    await page.fill('input[placeholder="请输入密码"]', testUser.password);
    await page.click('button:has-text("登录")');

    // 验证登录成功
    await page.waitForURL('/', { timeout: 20000 });
    await expect(page).toHaveURL('/');
  });

  test('登录失败应该显示错误信息', async ({ page }) => {
    await page.goto('/auth');

    // 使用错误的密码
    await page.fill('input[placeholder="请输入用户名"]', 'nonexistent_user');
    await page.fill('input[placeholder="请输入密码"]', 'wrongpassword');
    await page.click('button:has-text("登录")');

    // 应该看到错误提示 - Element Plus 使用 el-message 类
    await page.waitForSelector('.el-message--error, .el-message', { timeout: 3000 });
  });

  test('未登录应该无法访问首页', async ({ page }) => {
    // 清除 localStorage
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.clear();
    });

    // 尝试访问首页
    await page.goto('/');

    // 应该重定向到登录页
    await page.waitForURL('/auth');
    await expect(page.locator('h2')).toContainText('登录');
  });

  test('已登录访问登录页应该重定向到首页', async ({ page }) => {
    // 每个测试生成唯一的用户名
    const randomSuffix = Math.floor(Math.random() * 1000000);
    const testUser = {
      username: `testuser_${randomSuffix}`,
      password: 'testpass123'
    };

    // 先注册并登录
    await page.goto('/auth');
    await page.click('text=立即注册');
    await page.fill('input[placeholder="请输入用户名"]', testUser.username);
    await page.fill('input[placeholder="请输入密码（至少6位）"]', testUser.password);
    await page.fill('input[placeholder="请再次输入密码"]', testUser.password);
    await page.click('button:has-text("注册")');
    await page.waitForURL('/', { timeout: 20000 });

    // 尝试访问登录页
    await page.goto('/auth');

    // 应该重定向到首页
    await page.waitForURL('/');
    await expect(page).toHaveURL('/');
  });

  test('退出登录应该清除认证状态', async ({ page }) => {
    // 每个测试生成唯一的用户名
    const randomSuffix = Math.floor(Math.random() * 1000000);
    const testUser = {
      username: `testuser_${randomSuffix}`,
      password: 'testpass123'
    };

    // 先注册并登录
    await page.goto('/auth');
    await page.click('text=立即注册');
    await page.fill('input[placeholder="请输入用户名"]', testUser.username);
    await page.fill('input[placeholder="请输入密码（至少6位）"]', testUser.password);
    await page.fill('input[placeholder="请再次输入密码"]', testUser.password);
    await page.click('button:has-text("注册")');
    await page.waitForURL('/', { timeout: 20000 });

    // 验证已登录
    const tokenBefore = await page.evaluate(() => localStorage.getItem('token'));
    expect(tokenBefore).not.toBeNull();

    // 退出登录（使用圆形按钮的选择器）
    await page.click('.el-header .el-button--circle');
    await page.waitForURL('/auth', { timeout: 5000 });

    // 验证 Token 已清除
    const tokenAfter = await page.evaluate(() => localStorage.getItem('token'));
    expect(tokenAfter).toBeNull();
  });

  test('刷新页面应该保持登录状态', async ({ page }) => {
    // 每个测试生成唯一的用户名
    const randomSuffix = Math.floor(Math.random() * 1000000);
    const testUser = {
      username: `testuser_${randomSuffix}`,
      password: 'testpass123'
    };

    // 先注册并登录
    await page.goto('/auth');
    await page.click('text=立即注册');
    await page.fill('input[placeholder="请输入用户名"]', testUser.username);
    await page.fill('input[placeholder="请输入密码（至少6位）"]', testUser.password);
    await page.fill('input[placeholder="请再次输入密码"]', testUser.password);
    await page.click('button:has-text("注册")');
    await page.waitForURL('/', { timeout: 20000 });

    // 刷新页面
    await page.reload();

    // 应该仍然在首页（保持登录状态）
    await page.waitForURL('/');
    await expect(page).toHaveURL('/');
  });
});
