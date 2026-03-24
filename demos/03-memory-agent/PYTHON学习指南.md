# Python 项目学习指南

> 本指南专为不熟悉 Python 的开发者编写，帮助你快速理解 Demo 2 项目的后端代码。

---

## 目录

1. [Python 基础速成](#1-python-基础速成)
2. [项目结构解析](#2-项目结构解析)
3. [核心概念详解](#3-核心概念详解)
4. [关键文件解读](#4-关键文件解读)
5. [学习路径](#5-学习路径)
6. [实践练习](#6-实践练习)

---

## 1. Python 基础速成

### 1.1 变量和数据类型

```python
# 变量赋值（不需要声明类型）
name = "张三"
age = 25
is_active = True
price = 99.9

# f-string 格式化字符串（Python 3.6+）
message = f"用户 {name}，年龄 {age}，状态 {is_active}"

# 列表（类似 JavaScript 的数组）
items = [1, 2, 3, 4, 5]
items.append(6)           # 添加元素
first_item = items[0]     # 访问元素（索引从 0 开始）

# 字典（类似 JavaScript 的对象）
user = {
    "name": "张三",
    "age": 25,
    "email": "zhang@example.com"
}
user["phone"] = "123456"  # 添加键值对
name = user["name"]        # 获取值
```

### 1.2 函数定义

```python
# 基本函数
def greet(name):
    return f"你好，{name}！"

# 带默认参数的函数
def create_user(username, is_active=True):
    return {"username": username, "is_active": is_active}

# 调用函数
message = greet("张三")
user = create_user("admin")  # 使用默认值
```

### 1.3 类和对象

```python
class User:
    # 类属性（所有实例共享）
    species = "人类"

    # 构造函数（创建对象时调用）
    def __init__(self, name, age):
        # 实例属性（每个实例独有）
        self.name = name
        self.age = age

    # 实例方法
    def greet(self):
        return f"你好，我是 {self.name}"

    # 类方法（不需要实例就能调用）
    @classmethod
    def get_species(cls):
        return cls.species

# 使用类
user = User("张三", 25)      # 创建对象
print(user.greet())          # 调用方法
print(user.name)             # 访问属性
```

### 1.4 异步编程（重要！）

```python
import asyncio

# 异步函数（可以并发执行）
async def fetch_user(user_id: int) -> dict:
    # 模拟异步操作（如网络请求）
    await asyncio.sleep(1)  # 等待 1 秒
    return {"id": user_id, "name": "张三"}

# 调用异步函数
async def main():
    # 并发执行多个异步操作
    users = await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3)
    )
    return users

# 运行异步函数
asyncio.run(main())
```

### 1.5 类型注解（Python 3.5+）

```python
from typing import List, Dict, Optional, Any

# 基本类型注解
def add(a: int, b: int) -> int:
    return a + b

# 复杂类型注解
def process_users(users: List[Dict[str, Any]]) -> List[str]:
    """处理用户列表，返回用户名列表"""
    return [user["name"] for user in users]

# 可选类型（可能为 None）
def find_user(user_id: int) -> Optional[Dict]:
    # 如果找不到返回 None
    return None
```

### 1.6 异常处理

```python
try:
    # 可能出错的代码
    result = 10 / 0
except ZeroDivisionError as e:
    # 捕获特定异常
    print(f"除零错误: {e}")
except Exception as e:
    # 捕获所有异常
    print(f"未知错误: {e}")
else:
    # 没有异常时执行
    print("计算成功")
finally:
    # 无论是否有异常都执行
    print("清理资源")
```

---

## 2. 项目结构解析

### 2.1 完整目录树

```
backend/
├── app/                    # 应用主目录
│   ├── __init__.py        # 包标识文件（告诉 Python 这是一个包）
│   ├── main.py            # FastAPI 应用入口
│   ├── config.py          # 配置管理
│   ├── models.py          # 数据模型定义
│   │
│   ├── agent/             # Agent 模块
│   │   ├── __init__.py
│   │   ├── base.py        # Agent 核心类
│   │   └── tools.py       # 工具定义
│   │
│   ├── providers/         # LLM 提供商
│   │   ├── __init__.py
│   │   ├── base.py        # LLM 客户端基类
│   │   └── zhipuai.py     # 智谱 AI 实现
│   │
│   ├── api/               # API 路由
│   │   ├── __init__.py
│   │   ├── chat.py        # 聊天端点
│   │   ├── auth.py        # 认证端点
│   │   ├── sessions.py    # 会话管理
│   │   └── health.py      # 健康检查
│   │
│   ├── auth/              # 认证模块
│   │   ├── __init__.py
│   │   ├── jwt.py         # JWT 令牌处理
│   │   ├── password.py    # 密码哈希
│   │   ├── dependencies.py# FastAPI 依赖注入
│   │   └── repository.py  # 用户数据访问
│   │
│   └── db/                # 数据库模块
│       ├── __init__.py
│       ├── connection.py  # 数据库连接池
│       └── repositories.py# 数据访问层
│
├── tests/                 # 测试目录
│   ├── __init__.py
│   ├── test_agent.py      # Agent 测试
│   ├── test_providers.py  # Provider 测试
│   └── ...
│
├── migrations/            # 数据库迁移文件
│   └── 001_initial_schema.sql
│
├── pyproject.toml        # 项目配置（类似 package.json）
├── pytest.ini            # pytest 配置
└── run_migration.py      # 运行数据库迁移
```

### 2.2 关键文件说明

#### `__init__.py` 文件
```python
# 这个文件可以是空的，但必须存在
# 它告诉 Python：这个目录是一个包

# 也可以在包初始化时导入常用类
from .agent.base import Agent
from .providers.zhipuai import ZhipuClient
```

#### `pyproject.toml` 文件（类似 package.json）
```toml
[project]
name = "web-agent-backend"
version = "0.1.0"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "asyncpg>=0.29.0",
    # ... 更多依赖
]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

---

## 3. 核心概念详解

### 3.1 Async/Await（异步编程）

**为什么需要异步？**
```python
# 同步代码（阻塞）
def sync_request():
    response = requests.get("https://api.example.com")  # 等待...
    return response

# 异步代码（非阻塞）
async def async_request():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com")  # 不阻塞
        return response
```

**关键概念**：
- `async def`: 定义异步函数
- `await`: 等待异步操作完成（期间可以执行其他任务）
- `asyncio.gather()`: 并发执行多个异步任务

### 3.2 FastAPI 依赖注入

```python
from fastapi import Depends, Header

# 依赖函数
def get_token(authorization: str = Header(...)):
    """从请求头提取 token"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "无效的认证格式")
    return authorization[7:]

# 使用依赖
@app.get("/users/me")
async def get_current_user(token: str = Depends(get_token)):
    """FastAPI 会自动调用 get_token() 并传入 token"""
    return {"token": token}
```

### 3.3 Pydantic 数据验证

```python
from pydantic import BaseModel, Field, validator

class UserCreate(BaseModel):
    """用户创建请求模型"""
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=6)
    email: str = Field(..., regex=r"^[^@]+@[^@]+\.[^@]+$")

    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('用户名只能包含字母和数字')
        return v

# FastAPI 自动验证
@app.post("/users")
async def create_user(user: UserCreate):
    # 如果数据无效，FastAPI 自动返回 422 错误
    return {"username": user.username}
```

### 3.4 连接池管理

```python
import asyncpg

class DatabasePool:
    _pool: asyncpg.Pool = None

    async def get_pool(self) -> asyncpg.Pool:
        """获取连接池（单例模式）"""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                "postgresql://user:pass@localhost/db",
                min_size=5,   # 最小连接数
                max_size=20   # 最大连接数
            )
        return self._pool

    async def execute(self, query: str, *args):
        """执行 SQL 查询"""
        pool = await self.get_pool()
        async with pool.acquire() as conn:  # 从连接池获取连接
            return await conn.execute(query, *args)
        # 连接自动归还到池中
```

---

## 4. 关键文件解读

### 4.1 `app/main.py` - 应用入口

```python
from fastapi import FastAPI
from app.api import chat, auth, sessions, health
from app.config import get_settings

# 创建 FastAPI 应用实例
app = FastAPI(
    title="Web Agent Demo",
    version="0.1.0",
    docs_url="/docs"  # Swagger UI 地址
)

# 注册路由（模块化设计）
app.include_router(chat.router, prefix="/api/chat")
app.include_router(auth.router, prefix="/api/auth")
app.include_router(sessions.router, prefix="/api/sessions")
app.include_router(health.router)

# 生命周期事件
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print("应用启动中...")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    print("应用关闭中...")
```

**学习要点**：
- FastAPI 应用由多个路由模块组成
- 使用 `include_router()` 注册子路由
- 生命周期事件用于初始化/清理资源

### 4.2 `app/agent/base.py` - Agent 核心逻辑

```python
class Agent:
    """Agent 类：负责管理对话和工具调用"""

    def __init__(self, provider: str, api_key: str, model: str):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.messages = []  # 消息历史

    async def process_message(self, message: str) -> AgentResponse:
        """处理用户消息（非流式）"""
        # 1. 添加用户消息
        self.messages.append({"role": "user", "content": message})

        # 2. 调用 LLM
        response = await self.client.chat(
            model=self.model,
            messages=self.messages
        )

        # 3. 检查是否需要调用工具
        if response.tool_calls:
            # 执行工具调用
            for tool_call in response.tool_calls:
                result = execute_tool(tool_call)
                self.messages.append({
                    "role": "user",
                    "content": f"工具结果: {result}"
                })
            # 递归调用，让 LLM 继续处理
            return await self.process_message("")

        # 4. 返回助手回复
        self.messages.append({
            "role": "assistant",
            "content": response.content
        })
        return AgentResponse(content=response.content)
```

**学习要点**：
- Agent 使用 ReAct 循环：思考 → 行动 → 观察 → 思考
- 消息历史维护对话上下文
- 工具调用实现扩展能力

### 4.3 `app/providers/zhipuai.py` - LLM 客户端

```python
import httpx

class ZhipuClient(LLMClient):
    """智谱 AI 客户端"""

    async def chat_stream(self, model, messages, tools=None):
        """流式聊天"""
        url = f"{self.base_url}/chat/completions"

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                url,
                json={
                    "model": model,
                    "messages": messages,
                    "stream": True
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as response:
                # 逐行读取 SSE 流
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        content = data["choices"][0]["delta"]["content"]
                        yield content
```

**学习要点**：
- 使用 `httpx` 进行异步 HTTP 请求
- `stream()` 方法处理流式响应
- `aiter_lines()` 逐行读取 SSE 格式

---

## 5. 学习路径

### 5.1 第一阶段：Python 基础（1-2 周）

**目标**：能够读懂 Python 代码

**学习资源**：
- [Python 官方教程（中文版）](https://docs.python.org/zh-cn/3/tutorial/)
- [廖雪峰 Python 教程](https://www.liaoxuefeng.com/wiki/1016959663602400)

**必掌握知识点**：
- ✅ 变量和数据类型
- ✅ 函数定义和调用
- ✅ 类和对象
- ✅ 列表和字典操作
- ✅ 异常处理
- ✅ 基本的文件 I/O

**实践练习**：
```python
# 练习 1：定义一个 User 类
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def to_dict(self):
        return {"name": self.name, "email": self.email}

# 练习 2：处理用户列表
def filter_active_users(users):
    """过滤出活跃用户"""
    return [u for u in users if u.get("is_active")]
```

### 5.2 第二阶段：异步编程（1 周）

**目标**：理解 async/await

**学习资源**：
- [Python asyncio 官方文档](https://docs.python.org/zh-cn/3/library/asyncio.html)
- [Real Python: Async IO in Python](https://realpython.com/async-io-python/)

**必掌握知识点**：
- ✅ `async def` 和 `await`
- ✅ 事件循环（event loop）
- ✅ 并发执行（`asyncio.gather`）
- ✅ 异步上下文管理器（`async with`）

**实践练习**：
```python
# 练习：并发请求多个 API
async def fetch_multiple_urls(urls):
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return responses
```

### 5.3 第三阶段：FastAPI 框架（1-2 周）

**目标**：能够理解项目结构

**学习资源**：
- [FastAPI 官方教程（中文版）](https://fastapi.tiangolo.com/zh/)
- [FastAPI 最佳实践](https://fastapi.tiangolo.com/zh/tutorial/)

**必掌握知识点**：
- ✅ 路由定义和请求方法
- ✅ 依赖注入系统
- ✅ Pydantic 数据验证
- ✅ 中间件和 CORS
- ✅ 异常处理

**实践练习**：
```python
# 练习：创建一个简单的 CRUD API
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

items = {}

@app.post("/items")
async def create_item(item: Item):
    item_id = len(items) + 1
    items[item_id] = item
    return {"id": item_id, **item.dict()}

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(404, "Item not found")
    return items[item_id]
```

### 5.4 第四阶段：项目实战（2 周）

**目标**：能够修改和扩展项目功能

**推荐实践**：
1. **添加新的 API 端点**
   ```python
   # 在 app/api/ 下创建新文件 stats.py
   @router.get("/stats")
   async def get_statistics():
       return {"total_users": 100, "active_users": 50}
   ```

2. **添加新的工具**
   ```python
   # 在 app/agent/tools.py 中添加
   @tool({
       "name": "weather",
       "description": "获取天气信息",
       "parameters": {
           "city": {"type": "string"}
       }
   })
   def get_weather(city: str) -> str:
       return f"{city} 今天晴天，温度 25°C"
   ```

3. **添加单元测试**
   ```python
   # 在 tests/ 下添加 test_weather.py
   def test_should_get_weather():
       result = get_weather("北京")
       assert "北京" in result
   ```

---

## 6. 实践练习

### 6.1 入门练习

**练习 1：理解数据流**
```python
# 任务：追踪一个聊天请求的完整流程
# 提示：
# 1. 从 frontend/src/api/chat.ts 开始
# 2. 到 backend/app/api/chat.py
# 3. 到 backend/app/agent/base.py
# 4. 到 backend/app/providers/zhipuai.py
# 5. 返回到前端

# 练习：画出这个流程图
```

**练习 2：读取配置**
```python
# 任务：创建一个函数读取配置
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_key: str

    class Config:
        env_file = ".env"

# 练习：
# 1. 创建 Settings 实例
# 2. 打印 database_url
# 3. 尝试访问不存在的配置会怎样？
```

### 6.2 进阶练习

**练习 3：添加新的 API 端点**
```python
# 任务：添加一个统计 API
# 在 backend/app/api/ 下创建 stats.py

from fastapi import APIRouter, Depends
from app.db.repositories import UserRepository

router = APIRouter(prefix="/api/stats", tags=["stats"])

@router.get("/users")
async def get_user_stats(user_repo: UserRepository = Depends()):
    """获取用户统计信息"""
    total = await user_repo.count()
    active = await user_repo.count_active()
    return {
        "total_users": total,
        "active_users": active
    }

# 练习：
# 1. 在 main.py 中注册这个路由
# 2. 测试这个端点
# 3. 添加更多统计信息
```

**练习 4：实现新的工具**
```python
# 任务：为 Agent 添加一个计算器工具
# 在 backend/app/agent/tools.py 中添加

def calculator(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {e}"

# 练习：
# 1. 将这个函数注册为工具
# 2. 测试 Agent 能否正确调用
# 3. 添加错误处理（防止执行恶意代码）
```

### 6.3 挑战练习

**练习 5：实现会话历史持久化**
```python
# 任务：将会话历史保存到数据库
# 提示：
# 1. 在 migrations/ 中创建表结构
# 2. 在 repositories.py 中添加方法
# 3. 在 agent/base.py 中保存历史

class MessageRepository:
    async def save_message(self, session_id: str, message: dict):
        """保存消息到数据库"""
        # TODO: 实现这个方法
        pass

    async def get_history(self, session_id: str):
        """获取会话历史"""
        # TODO: 实现这个方法
        pass
```

---

## 7. 常见问题解答

### Q1: Python 的 `self` 是什么？

```python
class User:
    def __init__(self, name):
        self.name = name  # self.name 是实例属性
        # name 是参数

# 类比 JavaScript：
class User {
    constructor(name) {
        this.name = name;  // this 类似 Python 的 self
    }
}
```

### Q2: `await` 和 `return` 的区别？

```python
async def fetch_data():
    # await: 等待异步操作完成，但不阻塞其他任务
    data = await database.query("SELECT * FROM users")
    # return: 返回结果，结束函数
    return data
```

### Q3: `->` 是什么？

```python
def add(a: int, b: int) -> int:
    #       ↑ 类型注解   ↑ 返回类型注解
    return a + b

# 这只是提示，不影响运行
# 类似 TypeScript 的类型注解
```

### Q4: `*args` 和 `**kwargs` 是什么？

```python
def func(*args, **kwargs):
    # args: 位置参数元组 (1, 2, 3)
    # kwargs: 关键字参数字典 {"a": 1, "b": 2}

func(1, 2, 3, a=1, b=2)
```

---

## 8. 调试技巧

### 8.1 使用 pdb 调试器

```python
import pdb

def my_function():
    pdb.set_trace()  # 设置断点
    # 程序会在这里暂停，可以检查变量
    x = 1
    y = 2
    return x + y
```

### 8.2 使用 logging

```python
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_message(message: str):
    logger.info(f"处理消息: {message}")  # 信息日志
    try:
        result = await do_something(message)
        logger.debug(f"处理结果: {result}")  # 调试日志
    except Exception as e:
        logger.error(f"处理失败: {e}")  # 错误日志
```

### 8.3 使用 FastAPI 自动文档

访问 `http://localhost:8000/docs` 查看：
- 所有 API 端点
- 请求/响应格式
- 在线测试工具

---

## 9. 推荐资源

### 官方文档
- [Python 官方文档](https://docs.python.org/zh-cn/3/)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/zh/)
- [Pydantic 文档](https://docs.pydantic.dev/)

### 学习网站
- [Real Python](https://realpython.com/) - 优质 Python 教程
- [Python Morsels](https://www.pythonmorsels.com/) - 进阶技巧

### 书籍推荐
- 《Python 编程：从入门到实践》
- 《流畅的 Python》
- 《Effective Python》

---

## 10. 下一步

完成学习后，你可以：

1. **阅读项目代码**：从 `main.py` 开始，按调用顺序阅读
2. **运行测试**：`pytest tests/ -v` 查看测试用例
3. **修改代码**：尝试添加新功能或修复 bug
4. **查看日志**：运行应用时观察日志输出

---

*祝你学习顺利！如有问题，随时询问。*

*文档版本：1.0*
*更新日期：2026-03-22*
