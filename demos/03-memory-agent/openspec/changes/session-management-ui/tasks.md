# Tasks: 会话管理 UI

## 实施顺序

```
┌─────────────────────────────────────────────────────────────────┐
│                       任务依赖图                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 数据库迁移                                                 │
│     │                                                          │
│     ▼                                                          │
│  2. 后端 Repository 扩展                                        │
│     │                                                          │
│     ▼                                                          │
│  3. 后端 API 扩展                                              │
│     │                                                          │
│     ├──────────────────┬──────────────────┐                    │
│     ▼                  ▼                  ▼                    │
│  4. 前端 API 客户端   5. sessionStore    6. 前端组件          │
│     │                  │                  │                    │
│     └──────────────────┴──────────────────┘                    │
│                             │                                  │
│                             ▼                                  │
│  7. 集成测试 + 文档更新                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Task 1: 数据库迁移 [feat, 30min]

**文件：** `backend/migrations/002_add_session_title.sql`

**内容：**
```sql
-- 添加会话标题字段
ALTER TABLE sessions
ADD COLUMN title VARCHAR(200) NOT NULL DEFAULT '新对话';

-- 创建优化索引
CREATE INDEX idx_sessions_user_updated
ON sessions(user_id, updated_at DESC);
```

**验证：**
```bash
psql $DATABASE_URL -f migrations/002_add_session_title.sql
```

**验收标准：**
- [ ] sessions 表包含 title 字段
- [ ] 现有会话的 title 默认为 "新对话"
- [ ] 索引创建成功

---

## Task 2: 后端 Repository 扩展 [feat, 1h]

**文件：** `backend/app/db/repositories.py`

**修改内容：**

1. **Session 模型添加 title 字段**
```python
class Session:
    def __init__(
        self,
        id: str,
        user_id: str,
        title: str,  # 新增
        created_at: datetime,
        updated_at: datetime
    ):
        # ...
```

2. **新增 SessionPreview 模型**
```python
class SessionPreview:
    """会话预览（用于列表）"""
    def __init__(
        self,
        id: str,
        title: str,
        last_message: str,
        message_count: int,
        updated_at: datetime
    ):
        # ...
```

3. **SessionRepository 新增方法**
```python
async def update_title(self, session_id: str, title: str) -> Session:
    """更新会话标题"""

async def find_with_preview(self, user_id: str) -> List[SessionPreview]:
    """获取会话列表（含最后一条消息预览）"""
```

**验收标准：**
- [ ] Repository 方法实现完成
- [ ] 单元测试通过

**测试文件：** `backend/tests/test_session_repository.py`（扩展）

---

## Task 3: 后端 API 扩展 [feat, 1.5h]

**文件：** `backend/app/api/sessions.py`

**新增端点：**

1. **PUT /api/sessions/{id}/title**
```python
@router.put("/{session_id}/title")
async def update_session_title(
    session_id: str,
    request: TitleUpdateRequest,
    current_user: TokenPayload = Depends(get_current_user)
):
    """更新会话标题"""
```

**修改现有端点：**

1. **GET /api/sessions**
   - 返回 SessionPreview 列表（含 last_message, message_count）

2. **GET /api/sessions/{id}**
   - 返回值包含 title 字段

**新增模型：** `backend/app/models.py`
```python
class TitleUpdateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)

class SessionPreview(BaseModel):
    id: str
    title: str
    last_message: str
    message_count: int
    updated_at: datetime
```

**验收标准：**
- [ ] PUT /api/sessions/{id}/title 工作正常
- [ ] GET /api/sessions 返回预览信息
- [ ] API 测试通过

**测试文件：** `backend/tests/test_sessions_api.py`（扩展）

---

## Task 4: 前端 API 客户端 [feat, 45min]

**文件：** `frontend/src/api/sessions.ts`（新建）

**内容：**
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

export interface SessionDetail extends Session {
  messages: Message[]
}

export async function getSessions(): Promise<Session[]>
export async function getSession(id: string): Promise<SessionDetail>
export async function createSession(): Promise<Session>
export async function deleteSession(id: string): Promise<void>
export async function updateSessionTitle(id: string, title: string): Promise<Session>
```

**修改文件：** `frontend/src/api/types.ts`
- 添加 Session 相关类型定义

**验收标准：**
- [ ] API 函数实现完成
- [ ] 类型定义正确

---

## Task 5: sessionStore 状态管理 [feat, 1h]

**文件：** `frontend/src/stores/sessionStore.ts`（新建）

**内容：**
```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Session } from '@/api/sessions'
import * as sessionsApi from '@/api/sessions'

export const useSessionStore = defineStore('session', () => {
  const sessions = ref<Session[]>([])
  const currentSessionId = ref<string | null>(null)
  const isLoading = ref(false)

  async function loadSessions() { /* ... */ }
  async function switchSession(sessionId: string) { /* ... */ }
  async function createSession() { /* ... */ }
  async function updateSessionTitle(sessionId: string, title: string) { /* ... */ }
  async function deleteSession(sessionId: string) { /* ... */ }
  function getCurrentSession() { /* ... */ }

  return {
    sessions,
    currentSessionId,
    isLoading,
    loadSessions,
    switchSession,
    createSession,
    updateSessionTitle,
    deleteSession,
    getCurrentSession
  }
})
```

**修改文件：** `frontend/src/stores/chat.ts`
- 移除 sessionId 管理
- 保留消息相关逻辑

**验收标准：**
- [ ] sessionStore 实现完成
- [ ] 单元测试通过

**测试文件：** `frontend/src/stores/__tests__/sessionStore.spec.ts`

---

## Task 6: 前端组件开发 [feat, 3h]

### Task 6.1: SessionItem 组件 [feat, 1h]

**文件：** `frontend/src/components/SessionItem.vue`（新建）

**功能：**
- 显示会话标题
- 显示最后一条消息预览
- 显示更新时间
- 悬停显示删除按钮
- 高亮当前会话

**Props：**
```typescript
interface Props {
  session: Session
  isActive: boolean
}
```

**Emits：**
```typescript
interface Emits {
  (e: 'select', id: string): void
  (e: 'delete', id: string): void
}
```

**验收标准：**
- [ ] 组件渲染正确
- [ ] 点击触发 select 事件
- [ ] 删除按钮触发 delete 事件
- [ ] 单元测试通过

**测试文件：** `frontend/src/components/__tests__/SessionItem.spec.ts`

---

### Task 6.2: SessionSidebar 组件 [feat, 1.5h]

**文件：** `frontend/src/components/SessionSidebar.vue`（新建）

**功能：**
- 显示会话列表
- 新建会话按钮
- 响应式布局
- 加载状态显示

**子组件：**
- SessionItem

**验收标准：**
- [ ] 会话列表正确渲染
- [ ] 新建按钮工作正常
- [ ] 会话切换正常
- [ ] 单元测试通过

**测试文件：** `frontend/src/components/__tests__/SessionSidebar.spec.ts`

---

### Task 6.3: 修改 HomeView 布局 [feat, 30min]

**文件：** `frontend/src/views/HomeView.vue`

**修改内容：**
```vue
<template>
  <div class="home-container">
    <SessionSidebar />
    <ChatContainer />
  </div>
</template>

<style scoped>
.home-container {
  display: flex;
  gap: 24px;
  /* ... */
}
</style>
```

**验收标准：**
- [ ] 侧边栏和聊天区域并排显示
- [ ] 响应式布局正常

---

### Task 6.4: 修改 ChatContainer [feat, 30min]

**文件：** `frontend/src/components/ChatContainer.vue`

**修改内容：**
- 移除 sessionId 管理（由 sessionStore 接管）
- 监听 currentSessionId 变化，加载对应消息
- 在切换会话时清空并重新加载消息

**验收标准：**
- [ ] 会话切换时消息正确加载
- [ ] 聊天功能正常

---

## Task 7: 后端单元测试 [test, 1.5h]

**文件：**
- `backend/tests/test_session_repository.py`（扩展）
- `backend/tests/test_sessions_api.py`（扩展）

**测试用例：**

**test_session_repository.py：**
```python
def test_update_title()
def test_find_with_preview()
def test_find_with_preview_empty_session()
def test_find_with_preview_multiple_sessions()
```

**test_sessions_api.py：**
```python
def test_update_session_title()
def test_update_session_title_too_long()
def test_update_nonexistent_session_title()
def test_get_sessions_returns_preview()
```

**验收标准：**
- [ ] 所有测试通过
- [ ] 覆盖率 ≥ 80%

---

## Task 8: 前端单元测试 [test, 1.5h]

**文件：**
- `frontend/src/stores/__tests__/sessionStore.spec.ts`
- `frontend/src/components/__tests__/SessionItem.spec.ts`
- `frontend/src/components/__tests__/SessionSidebar.spec.ts`

**测试用例：**

**sessionStore.spec.ts：**
```typescript
describe('sessionStore', () => {
  it('initializes with empty state')
  it('loads sessions from API')
  it('switches current session')
  it('creates new session')
  it('updates session title')
  it('deletes session')
  it('handles API errors')
})
```

**SessionItem.spec.ts：**
```typescript
describe('SessionItem', () => {
  it('renders session title')
  it('renders preview message')
  it('formats timestamp')
  it('emits select on click')
  it('shows delete button on hover')
  it('emits delete on delete click')
  it('highlights when active')
})
```

**SessionSidebar.spec.ts：**
```typescript
describe('SessionSidebar', () => {
  it('renders session list')
  it('creates new session')
  it('emits select event')
  it('emits delete event')
  it('shows loading state')
  it('highlights active session')
})
```

**验收标准：**
- [ ] 所有测试通过
- [ ] 覆盖率 ≥ 80%

---

## Task 9: 文档更新 [docs, 30min]

**文件：** `README.md`

**更新内容：**
- 更新功能特性列表
- 添加会话管理功能说明
- 更新 API 文档
- 更新截图（如有）

**验收标准：**
- [ ] 文档准确反映新功能
- [ ] API 文档完整

---

## Task 10: 端到端验证 [test, 30min]

**手动测试清单：**
- [ ] 登录后能看到会话列表
- [ ] 点击会话能切换
- [ ] 新建会话按钮工作正常
- [ ] 会话标题自动生成
- [ ] 可以手动编辑标题
- [ ] 删除会话有确认提示
- [ ] 切换会话后消息正确加载
- [ ] 响应式布局正常（移动端）

**自动化测试（可选）：**
- 添加 Playwright E2E 测试

---

## 总结

| 任务 | 类型 | 预估时间 | 依赖 |
|------|------|----------|------|
| 1. 数据库迁移 | feat | 30min | - |
| 2. Repository 扩展 | feat | 1h | 1 |
| 3. API 扩展 | feat | 1.5h | 2 |
| 4. 前端 API 客户端 | feat | 45min | - |
| 5. sessionStore | feat | 1h | 4 |
| 6.1 SessionItem | feat | 1h | 5 |
| 6.2 SessionSidebar | feat | 1.5h | 6.1 |
| 6.3 HomeView | feat | 30min | 6.2 |
| 6.4 ChatContainer | feat | 30min | 5 |
| 7. 后端测试 | test | 1.5h | 2,3 |
| 8. 前端测试 | test | 1.5h | 5,6.1,6.2 |
| 9. 文档更新 | docs | 30min | 全部 |
| 10. E2E 验证 | test | 30min | 全部 |

**总计：约 12.5 小时（~1.5 个工作日）**
