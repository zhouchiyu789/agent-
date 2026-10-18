# Python 项目语法补习（Java 后端转 Agent 版）

这份文档只讲当前 `agent_starter` 项目中会遇到的 Python 语法。目标不是学完 Python，而是能够独立阅读、修改和调试这个项目。

建议顺序：

1. 先学第 1～7 节，读懂普通 Python 代码。
2. 再学第 8～10 节，读懂异步调用和类型提示。
3. 然后学第 11～14 节，读懂 Pydantic、pytest、FastAPI 和 LangGraph。
4. 最后按第 15 节重新阅读项目。

每节使用同一种方法：先看语法和 Java 对照，再打开对应项目文件，最后完成自测。

---

## 1. 缩进、变量和基本类型

### 1.1 Python 用缩进表示代码块

Java 使用大括号：

```java
if (amount > 0) {
    System.out.println(amount);
}
```

Python 使用冒号和缩进：

```python
if amount > 0:
    print(amount)
```

通常使用 4 个空格。缩进层级不同，含义就不同：

```python
if amount > 0:
    print("金额有效")
    print(amount)

print("检查结束")
```

前两行属于 `if`，最后一行不属于。

### 1.2 变量不需要声明类型

```python
order_id = "A1001"
amount = 199.0
paid = True
result = None
```

常用类型：

| Python | Java 对应 |
| --- | --- |
| `str` | `String` |
| `int` | `int` / `long` |
| `float` | `double` |
| `bool` | `boolean` |
| `None` | `null` |

Python 布尔值首字母大写：`True`、`False`。空值写作 `None`。

### 1.3 f-string 字符串格式化

项目中经常看到：

```python
message = f"订单 {order_id}，金额 {amount:.2f} 元"
```

其中：

- `{order_id}`：把变量放进字符串。
- `{amount:.2f}`：保留两位小数。

类似 Java：

```java
String message = "订单 %s，金额 %.2f 元".formatted(orderId, amount);
```

### 本节自测

阅读 `agent_starter/mock_backend.py`，找出字符串、浮点数、字典和 `None`（如果存在）。

---

## 2. 集合与常用操作

### 2.1 list：有顺序、可以修改

```python
events = ["route:order_query", "tool:get_order:ok"]
events.append("answer:done")
first = events[0]
```

类似 Java 的 `ArrayList<String>`。

### 2.2 dict：键值对

```python
state = {
    "query": "帮我查 A1001",
    "events": [],
}

query = state["query"]
events = state.get("events", [])
```

区别：

- `state["missing"]`：键不存在时抛出 `KeyError`。
- `state.get("missing")`：键不存在时返回 `None`。
- `state.get("missing", [])`：键不存在时返回指定默认值。

类似 Java 的 `Map<String, Object>`。

### 2.3 tuple：通常表示固定结构

```python
retry_errors = (TimeoutError, ConnectionError)
```

项目中用它一次捕获多种异常：

```python
except (TimeoutError, ConnectionError) as exc:
    ...
```

### 2.4 解包

```python
first, second = ["A1001", "A1002"]
```

异步并发时也会看到：

```python
first, second = await asyncio.gather(load_first(), load_second())
```

### 本节自测

解释 `workflow.py` 中下面的返回值为什么是字典：

```python
return {"intent": intent, "events": [f"route:{intent}"]}
```

---

## 3. 条件、循环和表达式

### 3.1 条件判断

```python
if response.status_code == 404:
    raise OrderNotFound(order_id)
elif response.status_code == 401:
    raise PermissionError()
else:
    print("继续处理")
```

逻辑运算：

```python
if order is not None and order.amount > 0:
    ...

if status == "paid" or status == "shipped":
    ...

if not approved:
    ...
```

不要使用 `== None`，通常写：

```python
value is None
value is not None
```

### 3.2 三元表达式

项目中：

```python
return "execute" if state["approved"] else "reject"
```

等价于：

```python
if state["approved"]:
    return "execute"
else:
    return "reject"
```

### 3.3 for 循环与 range

```python
for attempt in range(1, attempts + 1):
    print(attempt)
```

如果 `attempts == 3`，依次得到 `1、2、3`。`range` 的结束值不包含在结果中。

### 3.4 指数运算

```python
delay = 0.1 * (2 ** (attempt - 1))
```

`**` 表示乘方，等待时间依次为 `0.1、0.2、0.4`。

### 本节自测

不用运行代码，写出 `attempts=4` 时每次重试前的等待时间。

---

## 4. 函数与参数

### 4.1 普通函数

```python
def extract_order_id(query: str) -> str | None:
    ...
```

- `def`：定义函数。
- `query`：参数。
- `: str`：参数类型提示。
- `-> str | None`：返回字符串或 `None`。

类型提示默认不会阻止程序运行，主要帮助 IDE、类型检查工具和阅读代码的人。

### 4.2 默认参数

```python
def connect(timeout: float = 5.0):
    ...
```

调用方式：

```python
connect()
connect(10.0)
connect(timeout=10.0)
```

### 4.3 `*` 后面的参数必须写名字

项目中的重试函数：

```python
async def call_with_retry(
    operation,
    *,
    attempts: int = 3,
    timeout_seconds: float = 5.0,
):
    ...
```

正确调用：

```python
await call_with_retry(load_order, attempts=3, timeout_seconds=2.0)
```

错误调用：

```python
await call_with_retry(load_order, 3, 2.0)
```

这种设计可以避免调用方记错多个数字参数的顺序。

### 4.4 函数也是对象

Python 可以把函数保存在变量中或传给另一个函数：

```python
def say_hello() -> str:
    return "hello"

operation = say_hello
result = operation()
```

注意区别：

```python
say_hello      # 函数本身，还没有执行
say_hello()    # 立即执行并得到返回值
```

`call_with_retry` 需要的是函数本身：

```python
await call_with_retry(load_order)
```

### 4.5 lambda：很短的匿名函数

测试中：

```python
transport = httpx.MockTransport(
    lambda request: httpx.Response(404)
)
```

等价于：

```python
def handler(request):
    return httpx.Response(404)

transport = httpx.MockTransport(handler)
```

类似 Java 的：

```java
request -> new Response(404)
```

### 4.6 嵌套函数和闭包

函数内部可以再定义函数：

```python
def create_counter():
    count = 0

    def increase():
        nonlocal count
        count += 1
        return count

    return increase
```

`nonlocal count` 表示修改外层函数中的变量，而不是创建新的局部变量。测试中的重试次数统计使用了这个语法。

### 本节自测

解释下面两种调用的区别：

```python
await call_with_retry(load_order)
await call_with_retry(load_order())
```

---

## 5. 类、对象和特殊方法

### 5.1 定义类

```python
class OrderClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def build_url(self, order_id: str) -> str:
        return f"{self.base_url}/orders/{order_id}"
```

Java 对照：

| Python | Java |
| --- | --- |
| `__init__` | 构造方法 |
| `self` | `this` |
| `self.base_url` | `this.baseUrl` |
| `client.build_url(...)` | `client.buildUrl(...)` |

Python 实例方法必须显式写 `self`，调用时不需要传它：

```python
client = OrderClient("http://localhost:8001")
url = client.build_url("A1001")
```

### 5.2 classmethod：类级工厂方法

项目中的配置类：

```python
@classmethod
def from_env(cls) -> "Settings":
    return cls(...)
```

调用：

```python
settings = Settings.from_env()
```

`cls` 表示当前类，类似一个可被子类继承的静态工厂方法。

### 5.3 dataclass：自动生成数据类代码

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    order_api_url: str
    api_key: str
```

`@dataclass` 自动生成构造方法、比较方法和字符串表示。`frozen=True` 表示创建后不能修改字段，接近 Java record。

### 本节自测

阅读 `agent_starter/config.py`，回答 `Settings.from_env()` 最后为什么可以写成 `cls(...)`。

---

## 6. 模块、包和 import

### 6.1 一个 `.py` 文件就是一个模块

```text
agent_starter/
├── __init__.py
├── config.py
└── order_client.py
```

导入项目代码：

```python
from agent_starter.config import Settings
from agent_starter.order_client import OrderClient
```

类似 Java 的包名加类名，但 Python 导入的是模块中的名称。

### 6.2 `__name__ == "__main__"`

```python
if __name__ == "__main__":
    main()
```

只有直接运行这个模块时才调用 `main()`：

```powershell
.\.venv\Scripts\python.exe -m agent_starter.cli A1001
```

如果别的模块只是 `import agent_starter.cli`，不会自动执行 `main()`。

### 6.3 `-m` 的含义

```powershell
.\.venv\Scripts\python.exe -m pytest
```

表示使用当前 Python 解释器运行指定模块。项目中优先使用这种写法，可以避免调用到错误环境中的命令。

---

## 7. 异常处理

### 7.1 定义和抛出异常

```python
class OrderNotFound(Exception):
    pass

raise OrderNotFound(order_id)
```

`pass` 表示这里不需要额外代码。这个异常类通过名字表达业务含义。

### 7.2 捕获异常

```python
try:
    response = await client.get(url)
except httpx.HTTPError as exc:
    raise OrderServiceError("订单服务不可用") from exc
```

一次捕获多个异常：

```python
except (httpx.HTTPError, ValueError, ValidationError) as exc:
    ...
```

### 7.3 `raise ... from exc` 保留异常链

```python
raise OrderServiceError("订单服务不可用") from exc
```

调用方只需要处理统一的业务异常，日志中仍然能看到最初是 HTTP、JSON 还是数据校验失败。

近似 Java：

```java
throw new OrderServiceException("订单服务不可用", cause);
```

### 7.4 为什么 404 单独处理

```python
if response.status_code == 404:
    raise OrderNotFound(order_id)

response.raise_for_status()
```

`404` 表示订单确实不存在，是明确业务结果；其他 `4xx/5xx` 暂时统一视为上游调用失败。

### 本节自测

阅读 `order_client.py`，说明以下三个失败分别会变成什么异常：

1. HTTP 404。
2. HTTP 500。
3. HTTP 200，但 JSON 缺少 `amount`。

---

## 8. with、async with 和资源释放

### 8.1 普通上下文管理器

```python
with open("example.txt") as file:
    content = file.read()
```

离开代码块时文件自动关闭，即使中途抛出异常也会关闭。类似 Java try-with-resources。

### 8.2 异步上下文管理器

```python
async with httpx.AsyncClient(timeout=5.0) as http_client:
    response = await http_client.get(url)
```

HTTP 客户端的创建和关闭包含异步操作，因此使用 `async with`。

### 8.3 pytest 中的异常上下文

```python
with pytest.raises(OrderNotFound):
    await client.get_order("missing")
```

含义是：代码块必须抛出 `OrderNotFound`，否则测试失败。

### 本节自测

解释为什么不能在每一次 HTTP 请求中随意创建新的 `AsyncClient`，并说明谁负责关闭当前项目中的客户端。

---

## 9. async、await 与事件循环

这是 Agent 后端最重要的 Python 知识。

### 9.1 定义协程

```python
async def load_order() -> Order:
    ...
```

直接调用不会立刻执行函数体：

```python
coroutine = load_order()
```

必须在异步环境中使用：

```python
order = await load_order()
```

### 9.2 启动事件循环

命令行程序通过：

```python
asyncio.run(show_order(order_id))
```

从同步世界进入异步世界。已经位于 `async def` 中时，直接使用 `await`，不要再次调用 `asyncio.run()`。

### 9.3 await 的真正含义

```python
response = await http_client.get(url)
```

等待网络期间，当前协程暂停，事件循环可以执行其他已经就绪的协程。它不会自动把普通阻塞代码变成非阻塞代码。

错误示例：

```python
async def wrong():
    time.sleep(5)  # 阻塞事件循环
```

正确示例：

```python
async def correct():
    await asyncio.sleep(5)
```

### 9.4 超时

```python
result = await asyncio.wait_for(
    operation(),
    timeout=5.0,
)
```

如果指定时间内没有完成，抛出 `TimeoutError`。

### 9.5 并发执行

```python
first, second = await asyncio.gather(
    client.get_order("A1001"),
    client.get_order("A1002"),
)
```

这适合彼此独立的 I/O 调用。它不是为 CPU 密集计算准备的线程池。

### 9.6 异步生成器

FastAPI 的 SSE 接口中：

```python
async def events():
    yield "event: message\ndata: first\n\n"
    await asyncio.sleep(0)
    yield "event: done\ndata: {}\n\n"
```

`yield` 每次产生一段数据，并保留函数当前状态，下一次继续从原位置运行。

普通 `return` 只返回一次并结束函数；`yield` 可以分多次产生结果。

### 本节自测

回答：

1. 调用 `load_order()` 为什么还没有发请求？
2. `await` 网络请求时，服务器为什么还能处理其他请求？
3. `time.sleep()` 为什么不能出现在异步请求链路中？
4. 哪些订单查询适合放进 `asyncio.gather()`？

---

## 10. 类型提示

### 10.1 类型提示默认不是运行时强制校验

```python
def double(value: int) -> int:
    return value * 2
```

Python 解释器通常不会仅因为传入错误类型而提前拒绝调用。类型提示主要提供：

- IDE 自动补全。
- 静态类型检查。
- 函数契约说明。
- Pydantic、FastAPI、LangGraph 等框架需要的元数据。

### 10.2 可空类型

```python
order_id: str | None
```

表示字符串或 `None`，接近 Java 的 `@Nullable String`。

### 10.3 容器类型

```python
list[str]
dict[str, object]
tuple[Order, Order]
```

### 10.4 Literal：限定几个字面值

```python
Intent = Literal["order_query", "general"]
```

它适合表达有限的字符串选项，但运行时是否校验取决于使用它的框架。

### 10.5 TypedDict：描述字典结构

```python
class AgentState(TypedDict, total=False):
    query: str
    answer: str
    events: list[str]
```

运行时它仍然是普通字典：

```python
state = {"query": "帮我查 A1001"}
```

`total=False` 表示所有字段都可以暂时缺少。LangGraph 中每个节点只返回自己更新的字段，因此适合这种状态。

### 10.6 Protocol：结构化接口

```python
class OrderReader(Protocol):
    async def get_order(self, order_id: str) -> Order: ...
```

实现类不需要写 `implements OrderReader`：

```python
class FakeOrders:
    async def get_order(self, order_id: str) -> Order:
        ...
```

只要方法结构匹配，就可以作为 `OrderReader` 使用。这使 HTTP 实现、MCP 实现和测试 Fake 可以互换。

### 10.7 Callable、Awaitable 和 TypeVar

```python
T = TypeVar("T")

operation: Callable[[], Awaitable[T]]
```

从内向外读：

1. `Callable[...]`：一个可调用对象，通常是函数。
2. `[]`：不接收参数。
3. `Awaitable[T]`：调用后得到可等待对象。
4. `T`：等待结束后得到的结果类型。

整体含义：`operation` 是一个无参数异步操作，最终返回某种 `T`。

### 10.8 Annotated

```python
events: Annotated[list[str], operator.add]
```

真实数据类型是 `list[str]`，`operator.add` 是给 LangGraph 的附加信息，告诉它合并状态时追加列表，而不是覆盖旧列表。

### 本节自测

解释 `OrderReader` 为什么既能接收真实 `OrderClient`，也能接收测试中的 `FakeOrders`。

---

## 11. Pydantic：运行时数据校验

Pydantic 会读取类型提示，并在运行时解析和校验数据。

### 11.1 定义模型

```python
from pydantic import BaseModel


class Order(BaseModel):
    order_id: str
    customer: str
    status: str
    amount: float
```

创建对象：

```python
order = Order(
    order_id="A1001",
    customer="张三",
    status="paid",
    amount=199.0,
)
```

### 11.2 校验外部字典

```python
data = response.json()
order = Order.model_validate(data)
```

执行顺序：

```text
HTTP 响应正文
→ response.json() 解析为 dict
→ Order.model_validate() 校验字段
→ 得到 Order 对象
```

缺字段或类型不符合要求时抛出 `ValidationError`。

### 11.3 序列化

```python
order.model_dump()             # 转为 dict
order.model_dump_json()        # 转为 JSON 字符串
order.model_dump_json(indent=2)
```

### 11.4 Field 约束

```python
from typing import Literal
from pydantic import BaseModel, Field


class Order(BaseModel):
    order_id: str = Field(min_length=1)
    customer: str = Field(min_length=1)
    status: Literal["created", "paid", "shipped", "cancelled"]
    amount: float = Field(ge=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
```

- `min_length=1`：不能为空字符串。
- `ge=0`：必须大于等于 0。
- `pattern=...`：必须匹配正则表达式。
- `Literal[...]`：只允许列出的状态。

### 11.5 dataclass 与 Pydantic 的选择

| 场景 | 建议 |
| --- | --- |
| 内部配置、简单数据容器 | `dataclass` |
| HTTP 请求和响应 | Pydantic `BaseModel` |
| 模型结构化输出 | Pydantic `BaseModel` |
| MCP 工具输入和输出 | Pydantic `BaseModel` |
| 需要 JSON 序列化或运行时校验 | Pydantic `BaseModel` |

### 本节自测

手动判断下面三个输入能否通过当前 `Order` 模型：

```python
{"order_id": "A1001", "customer": "张三", "status": "paid", "amount": 199}
{"order_id": "A1001"}
{"order_id": "A1001", "customer": "张三", "status": "paid", "amount": "abc"}
```

---

## 12. 装饰器与框架注册

### 12.1 先理解使用方式

```python
@pytest.mark.asyncio
async def test_get_order():
    ...
```

```python
@app.get("/health")
async def health():
    ...
```

```python
@dataclass(frozen=True)
class Settings:
    ...
```

现阶段把装饰器理解为：框架在函数或类定义完成后，对它进行注册或包装。

### 12.2 大致等价形式

```python
@decorator
def function():
    ...
```

大致等价于：

```python
def function():
    ...

function = decorator(function)
```

目前需要会读、会使用，不要求自己实现复杂装饰器。

---

## 13. pytest 与测试 Fake

### 13.1 测试函数

```python
def test_something() -> None:
    assert 1 + 1 == 2
```

pytest 会自动收集：

- 文件名以 `test_` 开头。
- 函数名以 `test_` 开头。

### 13.2 异步测试

```python
@pytest.mark.asyncio
async def test_get_order() -> None:
    order = await client.get_order("A1001")
    assert order.order_id == "A1001"
```

插件为测试提供事件循环，因此可以直接 `await`。

### 13.3 MockTransport

```python
transport = httpx.MockTransport(
    lambda request: httpx.Response(200, json={...})
)
```

它拦截 HTTP 请求并返回构造好的响应，不需要真的启动服务器。

### 13.4 Fake 对象

```python
class FakeOrders:
    async def get_order(self, order_id: str) -> Order:
        return Order(...)
```

Fake 实现项目需要的最小接口，使测试只关注当前逻辑。它与 Mockito mock 的目标相似，但代码更直接。

### 13.5 验证异常

```python
with pytest.raises(OrderServiceError):
    await client.get_order("A1001")
```

### 13.6 运行当前两组基础测试

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_order_client.py tests/test_reliability.py -vv -s
```

`-vv` 显示每条测试名，`-s` 允许显示代码中的标准输出。

### 本节自测

阅读 `tests/test_order_client.py`，分别说明三条测试模拟了什么上游响应，以及预期结果是什么。

---

## 14. FastAPI 和 LangGraph 中的特殊写法

### 14.1 FastAPI 路由

```python
@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    ...
```

接近 Spring：

```java
@GetMapping("/orders/{orderId}")
```

### 14.2 Depends 依赖注入

```python
async def order_summary(
    order_id: str,
    client: OrderClient = Depends(get_client),
):
    ...
```

FastAPI 调用 `get_client`，把结果传给 `client`。可以把它理解为方法参数级依赖注入。

### 14.3 lifespan 生命周期

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient() as client:
        app.state.client = client
        yield
```

执行顺序：

```text
服务启动
→ 创建 AsyncClient
→ yield 期间处理请求
→ 服务停止
→ 关闭 AsyncClient
```

`yield` 前相当于初始化，`yield` 后相当于销毁。

### 14.4 StreamingResponse 与 SSE

```python
async def events():
    yield "event: message\ndata: hello\n\n"
    yield "event: done\ndata: {}\n\n"

return StreamingResponse(events(), media_type="text/event-stream")
```

异步生成器逐段输出数据，客户端不需要等全部内容生成完。

### 14.5 LangGraph 节点是函数

```python
async def classify(state: AgentState) -> AgentState:
    intent = await router.route(state["query"])
    return {"intent": intent}
```

每个节点接收当前状态，返回需要更新的部分。

### 14.6 条件边

```python
builder.add_conditional_edges(
    "classify",
    lambda state: state["intent"],
    {
        "order_query": "query_order",
        "general": "answer_general",
    },
)
```

执行过程：

1. `classify` 节点结束。
2. Lambda 读取 `state["intent"]`。
3. 映射表决定下一个节点。

### 14.7 `...` 的含义

Protocol 中：

```python
class OrderReader(Protocol):
    async def get_order(self, order_id: str) -> Order: ...
```

`...` 是合法的 Python 对象 `Ellipsis`。这里表示只声明方法签名，不提供实现，类似 Java interface 中的方法声明。

---

## 15. 按难度重新阅读项目

### 阶段一：普通类、异常和 Pydantic

按顺序阅读：

1. `agent_starter/config.py`
2. `agent_starter/order_client.py`
3. `agent_starter/mock_backend.py`
4. `agent_starter/cli.py`

完成标准：能解释配置如何创建、HTTP 响应如何变成 `Order`、异常如何传到 CLI。

### 阶段二：异步测试和可靠性

按顺序阅读：

1. `tests/test_order_client.py`
2. `agent_starter/reliability.py`
3. `tests/test_reliability.py`

完成标准：能解释 MockTransport、`pytest.raises`、函数参数 `operation`、超时和重试。

### 阶段三：FastAPI

按顺序阅读：

1. `agent_starter/api.py`
2. `tests/test_api.py`
3. `agent_starter/agent_api.py`

完成标准：能解释路由、依赖注入、生命周期、异常映射和 SSE。

### 阶段四：LangGraph

按顺序阅读：

1. `agent_starter/workflow.py`
2. `tests/test_workflow.py`
3. `agent_starter/approval_workflow.py`

完成标准：能解释状态、节点、条件边、Protocol、checkpointer 和人工确认。

---

## 16. 五天补习安排

### 第 1 天：普通语法

- 阅读第 1～4 节。
- 阅读 `config.py` 和 `mock_backend.py`。
- 自己写一个接收订单号并返回字符串的函数。

### 第 2 天：类、模块和异常

- 阅读第 5～8 节。
- 逐行阅读 `order_client.py`。
- 画出 404、500、无效 JSON 三条异常路径。

### 第 3 天：异步

- 阅读第 9 节。
- 阅读 `cli.py` 和 `reliability.py`。
- 用自己的话解释 `async def`、`await`、`async with` 和 `wait_for`。

### 第 4 天：类型提示和 Pydantic

- 阅读第 10～11 节。
- 阅读 `workflow.py` 中的状态和 Protocol。
- 给 `Order` 增加 `currency` 字段并更新相关数据。

### 第 5 天：pytest、FastAPI 和 LangGraph

- 阅读第 12～15 节。
- 阅读三组测试。
- 运行完整测试并解释每条测试保护了什么行为。

运行命令：

```powershell
.\.venv\Scripts\python.exe -m pytest -vv
```

---

## 17. 最终过关清单

不看答案，能够解释下面问题，就可以继续学习模型调用和 Agent：

- [ ] `self` 和 Java 的 `this` 有什么关系？
- [ ] `function` 与 `function()` 有什么区别？
- [ ] `str | None` 表达什么？
- [ ] `with` 和 `async with` 分别解决什么问题？
- [ ] 为什么调用协程后还要 `await`？
- [ ] 为什么异步代码中不应使用 `time.sleep()`？
- [ ] `raise NewError() from exc` 为什么保留原异常？
- [ ] Pydantic 在什么时候执行真实校验？
- [ ] `TypedDict`、`Protocol` 和 `Literal` 分别解决什么问题？
- [ ] `Callable[[], Awaitable[T]]` 应该怎样从内向外阅读？
- [ ] `@pytest.mark.asyncio` 有什么作用？
- [ ] `Depends` 与 Spring 依赖注入有什么相似之处？
- [ ] `yield` 为什么可以用于 SSE 流式输出？
- [ ] LangGraph 节点为什么只返回部分状态？
- [ ] 取消订单为什么必须在工具调用前进行人工确认？

遇到陌生语法时，先按下面四步拆解：

1. 找出函数或类的输入。
2. 找出返回值。
3. 找出可能抛出的异常。
4. 找出需要创建和关闭的资源。

只要这四点能够说明白，就已经可以在项目中安全地继续学习和修改代码。
