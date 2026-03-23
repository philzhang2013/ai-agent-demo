# AI Agent Demo 项目配置

## 项目概述

AI Agent 学习项目，系统性学习和实践 AI Agent 开发。

**学习路径**：`命令行 Agent` → `Web Agent` → `聊天机器人` → `自动化工具`

**技术栈**：TypeScript/JS · ZhipuAI/MiniMax/Kimi · Vitest · npm

---

## 开发工作流 (MANDATORY)

⚠️ **严格遵守**：所有代码修改必须遵循以下工作流，**不得跳过任何步骤**。

```
1. PLAN    → 理解需求，明确验收标准
2. TEST    → 先写测试，描述预期行为（RED）
3. CODE    → 编写最小实现使测试通过（GREEN）
4. VERIFY  → 运行所有测试，确保通过
5. REVIEW  → 代码审查（自我审查或请求审查）
6. REFACTOR→ 优化代码，保持测试通过
7. REPORT  → 测试通过后才告知用户完成
```

---

## TDD 严格工作流 (MANDATORY)

### 规则 1: 测试优先原则

所有代码修改必须先写测试：`RED → GREEN → REFACTOR → VERIFY`

📖 [TDD 工作流详解](./docs/tdd-workflow.md)

### 规则 2: 测试通过后才能报告

完成代码修改后必须：
1. 运行单元测试：`npm test` 或 `pytest`
2. 确认全部通过 ✅
3. 检查覆盖率 ≥ 80%：`npm run test:coverage` 或 `pytest --cov`
4. 才告知用户完成

**禁止**：❌ 不运行测试直接报告 · ❌ 测试失败报告完成 · ❌ 跳过覆盖率检查

### 规则 3: 最小测试覆盖率：80%

📖 [测试类型和规范](./docs/testing-guide.md)

---

## Code Review 检查清单 (MANDATORY)

### 自我审查（提交前）

- [ ] 代码实现了需求描述的功能
- [ ] 测试覆盖正常和异常情况
- [ ] 测试覆盖率 ≥ 80%
- [ ] 命名清晰，函数职责单一
- [ ] 没有重复代码
- [ ] 错误处理完善
- [ ] 没有敏感信息（密钥、密码）
- [ ] 符合项目代码规范

📖 [Code Review 详细指南](./docs/code-review.md)

---

## 代码修改检查清单

**修改前**：
- [ ] 已理解需求和验收标准
- [ ] 已编写/更新测试用例
- [ ] 测试描述了预期行为
- [ ] 运行测试确认 RED 状态（如果新测试）

**修改后**：
- [ ] 所有测试通过 ✅
- [ ] 覆盖率 ≥ 80%
- [ ] 自我审查完成
- [ ] 没有引入新的警告
- [ ] 没有破坏现有功能
- [ ] 代码符合项目规范

**只有以上全部确认后，才能告知用户"完成"。**

---

## 技术约定

📖 [详细规范](./docs/coding-standards.md)

**核心原则**：
- 文件 200-400 行，最多 800 行
- 高内聚低耦合，按功能组织
- TypeScript 严格模式
- 显式错误处理，不吞没异常
- 不可变性：创建新对象，不修改原对象

---

## Git 提交规范 (MANDATORY)

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范。

📖 [Git 提交规范详细指南](./docs/git-commit-convention.md)

**快速参考**：

**格式**：`<type>: <description>`

**Type**：`feat` · `fix` · `refactor` · `docs` · `test` · `chore`

**示例**：
```
feat: 添加用户认证功能
fix: 修复聊天消息未保存
```

**推送前确认**：⚠️ **必须征得用户（爸爸）确认**

---

## 延迟加载文档

| 文档 | 说明 | 何时阅读 |
|------|------|----------|
| [TDD 工作流详解](./docs/tdd-workflow.md) | RED-GREEN-REFACTOR | 学习 TDD 时 |
| [测试类型和规范](./docs/testing-guide.md) | 单元/集成/E2E | 编写测试时 |
| [Code Review 指南](./docs/code-review.md) | Review 流程和标准 | 审查代码时 |
| [技术约定和代码规范](./docs/coding-standards.md) | 代码组织和命名 | 编码时参考 |
| [Git 提交规范](./docs/git-commit-convention.md) | Conventional Commits | 提交代码时 |
