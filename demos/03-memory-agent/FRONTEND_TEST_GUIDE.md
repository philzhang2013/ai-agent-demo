# 前端功能测试指南

## 服务状态
- ✅ 后端运行在：http://localhost:8000/
- ✅ 前端运行在：http://localhost:5173/
- ✅ API 文档：http://localhost:8000/docs

---

## 手动测试步骤

### 1. 测试用户注册

1. **打开浏览器访问：** http://localhost:5173/

2. **操作：**
   - 点击"注册"标签
   - 输入用户名（如：testuser）
   - 输入密码（如：password123）
   - 点击"注册"按钮

3. **预期结果：**
   - 显示成功提示
   - 自动跳转到聊天页面
   - 可以看到用户名显示

---

### 2. 测试用户登录

1. **打开浏览器访问：** http://localhost:5173/

2. **操作：**
   - 确保在"登录"标签
   - 输入已注册的用户名和密码
   - 点击"登录"按钮

3. **预期结果：**
   - 显示成功提示
   - 跳转到聊天页面
   - JWT Token 已保存（可在浏览器控制台验证）

---

### 3. 测试路由守卫

1. **测试未登录访问：**
   - 打开新的无痕窗口
   - 直接访问 http://localhost:5173/
   - **预期：** 自动跳转到登录页

2. **测试已登录访问登录页：**
   - 登录后访问 http://localhost:5173/auth
   - **预期：** 自动跳转到首页

---

### 4. 测试聊天功能

1. **发送消息：**
   - 在输入框输入："你好"
   - 点击发送按钮

2. **预期结果：**
   - 用户消息立即显示
   - AI 响应以流式方式逐字显示
   - 收到完成标记

---

### 5. 测试工具调用

1. **计算器测试：**
   - 输入："计算 18 + 25"
   - **预期：** 显示计算结果 43

2. **天气查询测试：**
   - 输入："查询北京的天气"
   - **预期：** 显示天气信息（当前为模拟数据）

---

### 6. 测试退出登录

1. **操作：**
   - 点击退出登录按钮

2. **预期结果：**
   - 清除认证状态
   - 跳转到登录页面
   - Token 已删除（浏览器控制台验证）

---

## 浏览器开发者工具验证

### 验证 JWT Token

1. 打开浏览器开发者工具（F12）
2. 进入 Application/应用 标签
3. 查看 Local Storage
4. 应该看到 `token` 键值对

### 验证 SSE 流

1. 打开浏览器开发者工具（F12）
2. 进入 Network/网络 标签
3. 发送聊天消息
4. 查看 `stream` 请求
5. 应该看到 EventStream 类型的响应

---

## 常见问题排查

### 问题：登录失败
**检查：**
1. 后端服务是否运行：`curl http://localhost:8000/api/health`
2. 浏览器控制台是否有错误
3. 网络请求是否成功

### 问题：SSE 不工作
**检查：**
1. 后端日志是否显示请求
2. 浏览器网络标签中 stream 请求状态
3. CORS 配置是否正确

### 问题：路由跳转异常
**检查：**
1. Pinia store 是否正确初始化
2. Token 是否存在于 localStorage
3. router 配置是否正确

---

## API 端点快速测试

```bash
# 健康检查
curl http://localhost:8000/api/health

# 注册用户
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"pass123"}'

# 登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"pass123"}'

# 获取当前用户（需要 Token）
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 发送消息（SSE 流式）
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"你好"}'
```
