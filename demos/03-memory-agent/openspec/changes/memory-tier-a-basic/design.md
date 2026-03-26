# 长短记忆分层 - 阶段A 设计文档

## 数据模型设计

### 新增表：memory_summaries

```sql
CREATE TABLE memory_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    content TEXT NOT NULL,           -- 摘要内容
    message_count INTEGER NOT NULL,  -- 总结了多少条消息
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(session_id)               -- 每个会话只有一个摘要
);

CREATE INDEX idx_memory_summaries_session ON memory_summaries(session_id);
```

### Pydantic模型

```python
class MemorySummary(BaseModel):
    """记忆摘要"""
    id: str
    session_id: str
    content: str
    message_count: int
    created_at: datetime
    updated_at: datetime

class MemorySummaryCreate(BaseModel):
    """创建记忆摘要请求"""
    content: str
    message_count: int
```

## 架构设计

### 核心组件

```
┌─────────────────────────────────────────────────────────┐
│                    MemoryManager                         │
├─────────────────────────────────────────────────────────┤
│  + should_summarize(session_id) -> bool                  │
│  + generate_summary(messages) -> str                     │
│  + get_context(session_id) -> List[Message]              │
└─────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │  Message   │  │  Summary   │  │    LLM     │
    │ Repository │  │ Repository │  │   Client   │
    └────────────┘  └────────────┘  └────────────┘
```

### MemoryManager 职责

1. **should_summarize(session_id)**: 检查是否需要生成摘要
  - 查询消息数 >= 5
  - 检查是否需要更新（消息数 >= 当前摘要.message_count + 5）
  - 首次生成或满足更新条件时返回 True
2. **generate_summary(messages)**: 调用LLM生成摘要
  - Prompt: "请总结以下对话的关键信息..."
3. **get_context(session_id)**: 获取发送给LLM的上下文
  - 如果有摘要：返回 [摘要] + [最近3条消息]
  - 无摘要：返回最近5条消息

## 流程设计

### 1. 发送消息流程（触发摘要）

```
用户发送消息
    │
    ▼
保存消息到数据库
    │
    ▼
调用 MemoryManager.should_summarize(session_id)
    │
    ├── 需要摘要 ──▶ 获取会话全部消息
    │                    │
    │                    ▼
    │              调用LLM生成摘要（基于全部消息）
    │                    │
    │                    ▼
    │              保存/更新摘要到数据库
    │                    - 首次：INSERT
    │                    - 更新：UPDATE（替换旧摘要）
    │
    └── 不需要 ────▶ 继续

触发条件：
- 首次：消息数 >= 5
- 更新：消息数 >= 当前摘要.message_count + 5

示例：
消息数=5  → 首次生成摘要（基于1-5）
消息数=10 → 更新摘要（基于1-10）
消息数=15 → 更新摘要（基于1-15）
...以此类推
```

### 2. 构建上下文流程

```
API接收到聊天请求
    │
    ▼
调用 MemoryManager.get_context(session_id)
    │
    ├── 有摘要 ────▶ 返回摘要 + 最近3条消息
    │
    └── 无摘要 ────▶ 返回最近5条消息
```

## 摘要生成Prompt

```
请对以下对话进行简洁总结，提取关键信息：

对话记录：
{messages}

总结要求：
1. 保留用户的主要意图和需求
2. 保留AI提供的关键建议和结论
3. 控制在100字以内
4. 使用第三人称客观描述

摘要：
```

## 错误处理


| 场景         | 处理策略                       |
| ---------- | -------------------------- |
| LLM摘要生成失败  | 记录错误，继续用原始消息，不重试，下次请求再尝试   |
| 数据库保存失败    | 抛出异常，回滚操作                  |
| 消息数正好为5条边界 | 使用 >= 5 条件触发               |
| 更新时并发冲突    | 使用数据库唯一约束，捕获冲突视为成功（保留先保存的） |
| 更新失败       | 保留旧摘要，下次请求再尝试更新            |


## # TDD 强制规范（MANDATORY）

## 1. 开发流程（必须遵守）

1. 必须先写测试（FAIL）

2. 再写实现（PASS）

3. 最后重构（REFACTOR）

## 2. 禁止行为

- 不允许先写实现代码

- 不允许没有测试的PR

- 不允许跳过失败测试

## 3. 测试覆盖

- 新功能必须包含测试

- 修改代码必须更新测试

## 4. 数据库测试

- 必须使用事务回滚

- 不允许共享测试数据

## 测试策略（严格TDD）

### 1. 先写测试，后实现代码

### 2. 测试覆盖要求

#### MemoryManager 单元测试

**正常路径：**

- `test_should_summarize_returns_true_when_5_messages_no_summary` - 首次触发
- `test_should_summarize_returns_true_when_10_messages_with_old_summary` - 更新触发
- `test_should_summarize_returns_false_when_less_than_5` - 不足不触发
- `test_should_summarize_returns_false_when_between_updates` - 5-9条不触发

**边界条件：**

- `test_should_summarize_at_exactly_5_messages` - 正好5条触发
- `test_should_summarize_at_exactly_10_messages` - 正好10条更新
- `test_should_summarize_at_6_to_9_messages` - 更新间隔内不触发
- `test_should_summarize_empty_session` - 空会话

**异常路径：**

- `test_generate_summary_handles_llm_error`
- `test_get_context_with_db_error`

#### Repository 测试

- `test_create_summary_success`
- `test_create_summary_duplicate_session`
- `test_find_by_session_id_exists`
- `test_find_by_session_id_not_exists`
- `test_update_summary_success`

#### API 集成测试

**验证点：**

- HTTP status code
- 返回数据结构
- 业务逻辑正确性
- 数据库副作用（摘要是否保存）

```python
# 示例：禁止只验证HTTP 200
def test_chat_triggers_summary():
    # 创建4条消息
    # 发送第5条（触发首次摘要）
    # 验证：
    # - HTTP 200
    # - 响应包含完整内容
    # - 数据库中新增了summary记录
    # - summary.message_count == 5
    # - summary.content 不为空

def test_chat_updates_summary():
    # 已有5条消息的摘要
    # 再发送5条消息（共10条，触发更新）
    # 验证：
    # - HTTP 200
    # - 数据库中summary记录被更新
    # - summary.message_count == 10（不是5）
    # - summary.updated_at 更新
```

## 任务分解

1. **测试先行 - Repository层**
  - 测试 MemorySummaryRepository
  - 实现 Repository
2. **测试先行 - MemoryManager**
  - 测试 should_summarize
  - 测试 generate_summary
  - 测试 get_context
  - 实现 MemoryManager
3. **测试先行 - API集成**
  - 测试聊天接口触发摘要
  - 测试上下文构建
  - 实现 API修改
4. **数据库迁移**
  - 创建 memory_summaries 表
5. **验证与文档**
  - 运行所有测试
  - 更新README

