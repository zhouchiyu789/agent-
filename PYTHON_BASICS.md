# Python 基础速查（Java 背景版）

配合本项目代码使用：每节只讲和 Java 差异大的部分，读完一节立刻去读对应的 `agent_starter/*.py`。目标不是"学完 Python"，而是能看懂并改动本项目。

---

## 1. 解释器与运行模型（先学这个，约 0.5 晚）

Python 没有 javac 编译步骤：`python.exe` 直接逐条解释执行 `.py` 文件。

### 概念对照

| Python | Java 对应 | 备注 |
| --- | --- | --- |
| `python.exe` | JVM（无需单独编译） | 机器上 `python` 命令可能指向旧版本，用完整路径最稳 |
| 虚拟环境 `.venv/` | 项目专属的 JDK + lib 目录 | 隔离每个项目的解释器和依赖，进入项目先激活/使用它 |
| `pip` | Maven | 但包装进当前 `.venv`，不是全局仓库 |
| `pyproject.toml` | `pom.xml` | 见下表 |
| `import xxx` | classpath + import | 按目录找模块；`agent_starter.config` = 包名.类名式路径 |
| `if __name__ == "__main__":` | `public static void main` | 只有直接运行该文件时才成立 |

### pyproject.toml ↔ pom.xml

| pyproject.toml | pom.xml |
| --- | --- |
| `[project]` name / version | `<artifactId>` / `<version>` |
| `requires-python = ">=3.11"` | `<java.version>` |
| `dependencies` | `<dependencies>` |
| `optional-dependencies` 的 `dev` | `scope=test` 依赖 |
| `-e ".[dev]"` 的 `-e` | 可编辑安装：改源码立即生效，不用重新 install |

### 逐条读懂 README 里的命令

```powershell
# 用 Python 3.14 在当前目录创建虚拟环境（= 生成 .venv 目录）
& 'D:\python1\python.exe' -m venv .venv

# -m pip = "把 pip 当模块运行"，强制用 .venv 里的 pip，避免 PATH 混淆
# install -e ".[dev]" = 以可编辑方式安装本项目，并额外装 dev 依赖(pytest)
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"

# -m pytest = 运行 pytest 模块；永远用 .venv 里的 python.exe 来跑
.\.venv\Scripts\python.exe -m pytest -q

# -m agent_starter.cli = 运行 agent_starter/cli.py，触发文件底部的 main()
.\.venv\Scripts\python.exe -m agent_starter.cli A1001

# -m uvicorn agent_starter.mock_backend:app = 启动 ASGI 服务器，加载 mock_backend.py 里的 app 对象
.\.venv\Scripts\python.exe -m uvicorn agent_starter.mock_backend:app --port 8001
```

### 自查

- 能说出 `.venv` 和全局 Python 的区别吗？
- `python -m agent_starter.cli` 和 `python agent_starter/cli.py` 有什么不同？
  - ✅ 已实验验证：直跑时 `sys.path[0]` 是脚本所在目录（找不到 `agent_starter` 包 → `ModuleNotFoundError`）；`-m` 时是当前目录（按包路径导入成功），且只有 `-m` 下相对导入 `from .config import ...` 才合法
  - 平时两者都能跑，是因为 `pip install -e` 生成的 `__editable__*.pth` 把包注册成了全局可导入，掩盖了差异
  - **结论：项目内跑模块永远用 `-m`**

---

## 2. async / await + asyncio（最重要，约 1 晚）

和 Java 的差异是本质性的：**Python 的 async 是单线程事件循环**，不是线程池。

### 核心规则

1. `async def f()` 定义协程。**调用 `f()` 不会执行任何代码**，只返回一个 coroutine 对象——这是新手第一大坑。
2. 必须用 `await f()` 才真正执行。`await` 处协程挂起，事件循环转去跑别的任务。
3. `asyncio.run(main())` 启动事件循环，是 async 世界的 main 入口。一个程序通常只调一次。
4. `async` 函数里不能直接调普通阻塞函数（会卡住整个事件循环）；要用异步版库（httpx.AsyncClient 而不是 requests）。

### 对照本项目代码

```python
# cli.py#L11-16
async def show_order(order_id: str) -> None:
    settings = Settings.from_env()
    # async with = 异步上下文管理器：退出时自动关闭连接（≈ try-with-resources）
    # 复用同一个 AsyncClient 走连接池，而不是每次请求新建 —— 这就是 README 验收问的"为什么复用和关闭"
    async with httpx.AsyncClient(timeout=5.0) as http_client:
        client = OrderClient(settings.order_api_url, http_client)
        order = await client.get_order(order_id)   # await 才真正发请求
```

```python
# cli.py#L25  同步 main() 里启动事件循环
asyncio.run(show_order(args.order_id))
```

```python
# reliability.py#L25-30  超时控制 + 指数退避
return await asyncio.wait_for(operation(), timeout=timeout_seconds)  # ≈ Future.get(timeout)
await asyncio.sleep(base_delay_seconds * (2 ** (attempt - 1)))       # 0.1s → 0.2s → 0.4s
```

### Java ↔ Python 对照

| Java | Python |
| --- | --- |
| `CompletableFuture.supplyAsync(...)` | `await coro()` |
| `future.get(5, TimeUnit.SECONDS)` | `asyncio.wait_for(coro(), timeout=5)` |
| `Thread.sleep(100)` | `await asyncio.sleep(0.1)`（不阻塞其他任务） |
| try-with-resources | `async with` / `with` |
| 线程池并发 | `asyncio.gather(*coros)` |

### 自查

- 为什么 `OrderClient` 里 `await self.http_client.get(...)` 期间其他请求还能被处理？
- 把 `asyncio.sleep` 换成 `time.sleep` 会发生什么？

---

## 3. 类型提示（读 workflow.py 前过一遍，约 0.5 晚）

关键认知：**类型提示运行时不强制，本质是给人和 IDE 看的注释**（pydantic 是唯一例外，它会真的校验）。和 Java 的静态检查完全相反。

### 对照本项目

```python
str | None                    # ≈ @Nullable String（3.10+ 语法，旧写法 Optional[str]）
Intent = Literal["order_query", "general"]   # ≈ 枚举的两个值，但只是字符串约束

# workflow.py#L14-19
class AgentState(TypedDict, total=False):    # ≈ 强类型的 Map<String,Object> 视图
    query: str
    events: Annotated[list[str], operator.add]  # LangGraph 元数据：新事件追加而非覆盖(reducer)

# workflow.py#L22-27
class IntentRouter(Protocol):                # ≈ interface，但不需要 implements
    async def route(self, query: str) -> Intent: ...  # 只要 duck-typing 匹配就自动符合

# reliability.py#L7
T = TypeVar("T")                             # ≈ <T> 泛型参数
```

### dataclass vs pydantic（项目里两种并存）

| | `@dataclass`（config.py） | `BaseModel`（order_client.py） |
| --- | --- | --- |
| 定位 | 纯数据容器，零依赖 | 数据容器 + **运行时校验** + JSON 序列化 |
| 类似 | Java record | Bean Validation + Jackson 合体 |
| 用途 | 内部配置 | 一切跨边界的数据（HTTP 请求/响应） |

`Order.model_validate(response.json())` 在这里做解析 + 校验，失败抛 `ValidationError`。

### 自查

- `AgentState` 里传入一个不存在的 key 会怎样？（total=False 时宽松；类型提示不会拦你）
- `Protocol` 和 Java interface 的最大区别？（无需显式声明实现关系）

---

## 4. 装饰器（10 分钟）

`@xxx` 本质就是 `f = xxx(f)`：拿原函数包一层再赋回原名。先会认会写，元编程以后再说。

```python
@dataclass(frozen=True)   # 自动生成 __init__ 等方法；frozen = 不可变（≈ record）
class Settings: ...

@classmethod              # 第一参数是类而不是实例（≈ 静态工厂）
def from_env(cls) -> "Settings": ...

@app.get("/orders/{order_id}")   # FastAPI：把函数注册成路由， Week 2 会大量见到
```

---

## 5. 现在开始的学习路线

| 顺序 | 做什么 | 产出 |
| --- | --- | --- |
| 晚 1 | 对照第 1 节逐条敲 README"环境准备"的 3 条命令，跑通 `pytest` | 解释每条命令在干什么 |
| 晚 1 剩余 | 读 `config.py` + `order_client.py`（很简单，15 分钟） | 说出 dataclass、异常映射、`from exc` 的作用 |
| 晚 2 | 两个窗口分别启动 mock_backend 和 cli，跑通 A1001 / missing | 对照第 2 节读懂 `cli.py` 全部 33 行 |
| 晚 2 剩余 | 读 `reliability.py`（32 行） | 说出重试策略和 `wait_for` 的行为 |
| 之后 | 回到 README 第 1 周计划，做练习 1、2 | 用 `str | None`、`Protocol` 读 `workflow.py` 就不费力了 |

遇到不懂的语法：直接问 AI"这行是什么语法"，即时查，别脱离上下文刷教程。
