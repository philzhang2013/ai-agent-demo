# 测试规范

> 本项目测试约定和 TDD 工作流

---

## 测试类型

| 类型 | 框架 | 位置 | 最低覆盖率 |
|------|------|------|-----------|
| 后端单元测试 | pytest | `backend/tests/` | 80% |
| 前端单元测试 | Vitest | `frontend/src/**/*.spec.ts` | 80% |
| 前端 E2E 测试 | Playwright | `frontend/e2e/` | 关键流程 |

---

## TDD 工作流

### 规则 1: 测试优先原则

所有代码修改必须先写测试：`RED → GREEN → REFACTOR`

```
1. RED    - 先写测试，运行测试失败
2. GREEN  - 编写最小实现使测试通过
3. REFACTOR - 重构优化，保持测试通过
4. VERIFY - 验证覆盖率 ≥ 80%
```

### 规则 2: 测试通过后才能报告

完成代码修改后必须：
1. 运行单元测试：`npm test` 或 `pytest`
2. 确认全部通过 ✅
3. 检查覆盖率 ≥ 80%：`npm run test:coverage` 或 `pytest --cov`
4. 才告知用户完成

**禁止**：
- ❌ 不运行测试直接报告
- ❌ 测试失败报告完成
- ❌ 跳过覆盖率检查

### 规则 3: 最小测试覆盖率：80%

---

## 后端测试 (pytest)

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_agent.py

# 显示详细输出
pytest -v

# 显示覆盖率
pytest --cov=app --cov-report=term-missing

# 生成 HTML 覆盖率报告
pytest --cov=app --cov-report=html
```

### 测试配置

`pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
```

---

## 前端测试 (Vitest)

### 运行测试

```bash
# 运行所有测试
npm test

# 运行特定文件
npm test -- MarkdownRenderer.spec.ts

# 监听模式
npm test -- --watch

# 覆盖率
npm run test:coverage

# UI 模式
npm test -- --ui
```

### 测试配置

`vitest.config.ts`:
```typescript
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      lines: 80,
      functions: 80,
      branches: 80,
      statements: 80,
    },
    environment: 'jsdom',  // 或 'happy-dom'
  },
})
```

---

## 测试编写规范

### 单元测试结构

```python
def test_feature_description():
    # Arrange - 准备测试数据
    input_data = {...}

    # Act - 执行被测试的功能
    result = function_under_test(input_data)

    # Assert - 验证结果
    assert result == expected_output
```

```typescript
describe('ComponentName', () => {
  it('should do something', () => {
    // Arrange
    const props = { ... }

    // Act
    const result = render(ComponentName, { props })

    // Assert
    expect(result.text()).toContain('expected')
  })
})
```

### 测试命名

- **清晰描述**：测试名称应清楚描述被测试的行为
- **应该式**：使用 `should` 或 `when...then...` 格式

```python
# 好的命名
def test_calculator_adds_two_numbers_correctly()
def test_user_login_fails_with_invalid_credentials()

# 不好的命名
def test_calculator()
def test_login()
```

---

## Mock 和 Fixture

### 后端 Mock (pytest)

```python
# conftest.py
@pytest.fixture
def mock_llm_client():
    with patch('app.providers.zhipuai.ZhipuAIClient') as mock:
        mock.return_value.chat.return_value = {"content": "test"}
        yield mock

# test_file.py
def test_agent_response(mock_llm_client):
    response = agent.process("hello")
    assert response.content == "test"
```

### 前端 Mock (vitest)

```typescript
// Component.spec.ts
vi.mock('@/api/chat', () => ({
  chatAPI: {
    sendMessage: vi.fn(() => Promise.resolve({ content: 'test' }))
  }
}))

describe('ChatComponent', () => {
  it('should send message', async () => {
    // ...
  })
})
```

---

## 集成测试

### 后端 API 测试

```python
def test_chat_endpoint(client):
    response = client.post("/api/chat", json={
        "message": "hello"
    })
    assert response.status_code == 200
    assert "content" in response.json()
```

### 前端 E2E 测试

```typescript
test('user can send message', async ({ page }) => {
  await page.goto('/chat')
  await page.fill('input[name="message"]', 'hello')
  await page.click('button[type="submit"]')
  await expect(page.locator('.message')).toContainText('hello')
})
```

---

## 调试测试

### 后端

```bash
# 进入调试模式
pytest --pdb

# 在失败时进入 pdb
pytest --pdb --trace

# 打印输出
pytest -s
```

### 前端

```bash
# 监听模式
npm test -- --watch

# 只运行匹配的测试
npm test -- -t "should add"

# 调试特定文件
npm test -- MarkdownRenderer.spec.ts --inspect-brk
```

---

## 常见问题

**Q: 测试失败时如何调试？**
- 使用 `pytest --pdb` 或 `npm test -- --inspect-brk`
- 添加 `print` 或 `console.log` 输出
- 检查 mock 和 fixture 是否正确

**Q: 覆盖率不达标怎么办？**
- 运行 `pytest --cov-report=html` 查看未覆盖代码
- 补充测试用例覆盖边界情况
- 检查是否有不可达代码

**Q: 测试运行太慢？**
- 使用 `@pytest.mark.skip` 跳过慢速测试
- 并行运行测试：`pytest -n auto`
- 使用 mock 避免真实 I/O 操作
