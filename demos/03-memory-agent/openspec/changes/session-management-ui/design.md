# Design: 会话管理 UI

## 架构概述

```
┌─────────────────────────────────────────────────────────────────┐
│                        整体布局                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┬─────────────────────────────────────────┐│
│  │  SessionSidebar  │         ChatContainer                    ││
│  │  (会话列表侧边栏) │         (聊天容器)                       ││
│  │                  │                                         ││
│  │  ┌────────────┐  │  ┌────────────────────────────────────┐ ││
│  │  │ + 新建会话  │  │  │ 当前会话标题                       │ ││
│  │  ├────────────┤  │  ├────────────────────────────────────┤ ││
│  │  │ 会话 1     │  │  │                                    │ ││
│  │  │ 会话 2     │◀─┼──┤  MessageList (消息列表)             │ ││
│  │  │ 会话 3     │  │  │                                    │ ││
│  │  │ ...        │  │  ├────────────────────────────────────┤ ││
│  │  └────────────┘  │  │ InputBox (输入框)                   │ ││
│  │                  │  │                                    │ ││
│  └──────────────────┴  └────────────────────────────────────┘ ││
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 数据库设计

### sessions 表扩展

```sql
-- 新增字段
ALTER TABLE sessions
ADD COLUMN title VARCHAR(200) NOT NULL DEFAULT '新对话';

-- 优化索引
CREATE INDEX idx_sessions_user_updated
ON sessions(user_id, updated_at DESC);
```

### 字段说明

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| title | VARCHAR(200) | '新对话' | 会话标题 |

## 后端设计

### API 扩展

#### 新增端点

```
PUT /api/sessions/{id}/title
```

**请求体：**
```json
{
  "title": "新会话标题"
}
```

**响应：**
```json
{
  "id": "uuid",
  "title": "新会话标题",
  "updated_at": "2026-03-24T11:30:00Z"
}
```

#### 修改现有端点返回值

**GET /api/sessions**

扩展返回值，添加标题和预览信息：

```json
{
  "sessions": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "title": "讨论天气查询功能",
      "last_message": "今天北京的天气怎么样？",
      "message_count": 5,
      "created_at": "2026-03-24T10:00:00Z",
      "updated_at": "2026-03-24T11:30:00Z"
    }
  ]
}
```

### Repository 扩展

```python
# app/db/repositories.py

class SessionRepository:
    async def update_title(self, session_id: str, title: str) -> Session:
        """更新会话标题"""
        # 实现略

    async def find_with_preview(self, user_id: str) -> List[SessionPreview]:
        """获取会话列表（包含最后一条消息预览）"""
        # 实现：需要 JOIN messages 表，获取最后一条消息
```

### 标题生成逻辑

**时机：** 首条用户消息保存后

**逻辑：**
```python
def generate_title(first_message: str) -> str:
    """
    从首条消息生成标题
    - 提取前 20 个字符
    - 如果超长，截断并添加 "..."
    - 去除首尾空白
    """
    title = first_message.strip()[:20]
    if len(first_message) > 20:
        title += "..."
    return title or "新对话"
```

## 前端设计

### 组件树

```
HomeView.vue
├── SessionSidebar.vue          # 新增
│   ├── SessionHeader.vue       # 新建按钮区域
│   └── SessionList.vue         # 会话列表
│       └── SessionItem.vue     # 新增（单个会话项）
└── ChatContainer.vue           # 修改（集成会话切换）
    ├── ChatHeader.vue          # 新增（当前会话标题）
    ├── MessageList.vue         # 复用
    └── InputBox.vue            # 复用
```

### 状态管理

**新建 `sessionStore.ts`：**

```typescript
interface SessionState {
  sessions: Session[]
  currentSessionId: string | null
  isLoading: boolean
}

interface Session {
  id: string
  title: string
  lastMessage: string
  messageCount: number
  updatedAt: Date
}

export const useSessionStore = defineStore('session', {
  state: (): SessionState => ({
    sessions: [],
    currentSessionId: null,
    isLoading: false
  }),

  actions: {
    // 加载会话列表
    async loadSessions(): Promise<void>

    // 切换会话
    async switchSession(sessionId: string): Promise<void>

    // 创建新会话
    async createSession(): Promise<Session>

    // 更新会话标题
    async updateSessionTitle(sessionId: string, title: string): Promise<void>

    // 删除会话
    async deleteSession(sessionId: string): Promise<void>

    // 获取当前会话
    getCurrentSession(): Session | null
  }
})
```

**现有 `chat.ts` 修改：**

- 移除 `sessionId` 管理（交由 sessionStore）
- 保留消息相关逻辑

### 组件设计

#### SessionSidebar.vue

**布局：**
```
┌────────────────────────────┐
│       会话历史              │
│  ┌──────────────────────┐  │
│  │  + 新建会话           │  │
│  └──────────────────────┘  │
│                            │
│  ┌──────────────────────┐  │
│  │ ● 会话 1             │  │
│  │   最后消息...        │  │
│  │   2小时前            │  │
│  ├──────────────────────┤  │
│  │ ○ 会话 2             │  │
│  │   最后消息...        │  │
│  │   昨天               │  │
│  └──────────────────────┘  │
└────────────────────────────┘
```

**关键交互：**
- 点击会话项 → 切换会话
- 点击新建 → 创建新会话并切换
- 悬停会话项 → 显示删除按钮

#### SessionItem.vue

**Props：**
```typescript
interface Props {
  session: Session
  isActive: boolean
}
```

**模板：**
```vue
<template>
  <div
    class="session-item"
    :class="{ active: isActive }"
    @click="$emit('select', session.id)"
  >
    <div class="session-title">{{ session.title }}</div>
    <div class="session-preview">{{ session.lastMessage }}</div>
    <div class="session-meta">
      <span class="session-time">{{ formattedTime }}</span>
      <el-button
        v-if="showDelete"
        :icon="Delete"
        circle
        size="small"
        @click.stop="$emit('delete', session.id)"
      />
    </div>
  </div>
</template>
```

### 数据流

```
┌──────────┐     ┌──────────────┐     ┌────────────┐
│  用户    │────▶│SessionSidebar│────▶│sessionStore│
│  点击    │     │              │     │            │
│  会话 B  │     └──────────────┘     └─────┬──────┘
└──────────┘                                 │
                                             │
                                             ▼
                                      ┌──────────────┐
                                      │ 1. 更新      │
                                      │   currentId  │
                                      │ 2. 调用 API  │
                                      │   获取消息   │
                                      │ 3. 通知      │
                                      │   chatStore  │
                                      └──────┬───────┘
                                             │
                                             ▼
                                      ┌──────────────┐
                                      │ChatContainer │
                                      │  重新渲染    │
                                      └──────────────┘
```

### API 客户端扩展

**新建 `api/sessions.ts`：**

```typescript
export interface Session {
  id: string
  user_id: string
  title: string
  last_message?: string
  message_count?: number
  created_at: string
  updated_at: string
}

export async function getSessions(): Promise<Session[]>
export async function getSession(id: string): Promise<Session & { messages: Message[] }>
export async function createSession(): Promise<Session>
export async function deleteSession(id: string): Promise<void>
export async function updateSessionTitle(id: string, title: string): Promise<Session>
```

## 边界情况处理

### 1. 会话切换时的并发问题

**问题：** 用户快速切换会话时，可能出现请求乱序

**解决方案：**
```typescript
// sessionStore 中记录当前请求 ID
let currentRequestId = 0

async switchSession(sessionId: string) {
  const requestId = ++currentRequestId
  // ... 发起请求

  // 只处理最新的请求响应
  if (requestId !== currentRequestId) return
}
```

### 2. 空会话列表

**处理：**
- 首次登录时自动创建一个会话
- 显示"暂无会话"提示

### 3. 会话删除确认

**处理：**
- 使用 Element Plus 的 `ElMessageBox.confirm`
- 提示"删除后无法恢复"

### 4. 网络错误处理

**处理：**
- 加载失败时显示错误提示
- 提供重试按钮
- 使用乐观更新提升体验

## 性能优化

### 1. 会话列表分页

**考虑：** 会话数量很多时（>100）

**方案：** 首次加载 50 个，滚动到底部加载更多

### 2. 消息加载优化

**当前：** 全量加载（Phase 1）

**未来优化（Phase 3）：**
- 分页加载历史消息
- 虚拟滚动

### 3. 标题生成防抖

```python
# 后端：避免短时间内重复生成标题
# 使用缓存或时间戳判断
```

## 样式设计

### 颜色规范

```css
/* 侧边栏 */
--sidebar-bg: #f5f7fa;
--sidebar-border: #e4e7ed;

/* 会话项 */
--session-item-bg: transparent;
--session-item-hover: #e9ecef;
--session-item-active: #fff;
--session-item-active-border: #667eea;

/* 文字 */
--title-color: #303133;
--preview-color: #909399;
--time-color: #c0c4cc;
```

### 响应式断点

```css
/* 大屏幕：侧边栏展开 */
@media (min-width: 768px) {
  .session-sidebar {
    width: 280px;
    display: flex;
  }
}

/* 小屏幕：侧边栏可折叠 */
@media (max-width: 767px) {
  .session-sidebar {
    position: fixed;
    width: 80%;
    max-width: 280px;
    transform: translateX(-100%);
    transition: transform 0.3s;
  }

  .session-sidebar.open {
    transform: translateX(0);
  }
}
```

## 测试策略

### 后端测试

**test_sessions_title.py**：
```python
def test_create_session_with_default_title()
def test_update_session_title()
def test_title_generation_from_first_message()
def test_title_too_long()
def test_update_nonexistent_session()
```

**test_session_repository.py**（扩展）：
```python
def test_find_with_preview()
def test_find_with_preview_empty_session()
def test_update_title()
```

### 前端测试

**SessionSidebar.spec.ts**：
```typescript
describe('SessionSidebar', () => {
  it('renders session list')
  it('creates new session on button click')
  it('emits select event when session clicked')
  it('highlights active session')
})
```

**SessionItem.spec.ts**：
```typescript
describe('SessionItem', () => {
  it('displays session title and preview')
  it('formats timestamp correctly')
  it('shows delete button on hover')
  it('emits delete event')
})
```

**sessionStore.spec.ts**：
```typescript
describe('sessionStore', () => {
  it('loads sessions from API')
  it('switches current session')
  it('creates new session')
  it('deletes session')
  it('updates session title')
})
```

## 迁移计划

1. **数据库迁移**：运行 `002_add_session_title.sql`
2. **后端部署**：部署新 API 和 Repository 修改
3. **前端部署**：部署新组件和状态管理
4. **验证**：测试所有功能端到端

## 回滚计划

如果出现问题：

1. **数据库**：`ALTER TABLE sessions DROP COLUMN title`
2. **后端**：恢复到 `sessions.py` 之前版本
3. **前端**：恢复 `HomeView.vue` 到之前版本（移除侧边栏）
