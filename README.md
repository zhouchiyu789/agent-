# Python Agent 学习项目：第 1～6 周

你已经有 Java 数字员工项目经验，这里直接用熟悉的“订单查询”场景练习 Python 服务开发。`mock_backend` 模拟现有 Java 订单接口；以后可以把 `ORDER_API_URL` 指向你自己的服务。本阶段的流式接口返回订单摘要，用来练习 SSE，还没有接入模型或 Agent 框架。

## 环境准备

需要 **Python 3.11 或更高版本**。这台机器当前 `python` 指向 Python 2.7，已安装的 Python 3.14 位于 `D:\python1\python.exe`，因此下面直接使用它创建虚拟环境。

在 PowerShell 中进入本目录，然后执行：

```powershell
& 'D:\python1\python.exe' -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
```

配置项直接通过环境变量读取；`.env.example` 是示例清单，不会被程序自动加载。默认 `APP_API_KEY=dev-token` 只用于本地练习。

## 第 1 周：Python 工程与异步调用

| 学习时段 | 任务 | 验收 |
| --- | --- | --- |
| 周二 1.5 小时 | 阅读 `config.py`、`order_client.py`，弄清数据模型、异常和 `async/await` | 能说明 `AsyncClient` 为什么需要复用和关闭 |
| 周四 1.5 小时 | 阅读 `cli.py`，启动模拟订单服务，运行命令行查询 | 正确订单可查询；不存在的订单返回明确错误 |
| 周末 4～6 小时 | 完成练习 1、2，运行测试并补一条故障用例 | 所有测试通过，能解释异常如何从 HTTP 层传到 CLI |

在第一个 PowerShell 窗口启动模拟后端：

```powershell
.\.venv\Scripts\python.exe -m uvicorn agent_starter.mock_backend:app --port 8001
```

在第二个窗口执行：

```powershell
.\.venv\Scripts\python.exe -m agent_starter.cli A1001
.\.venv\Scripts\python.exe -m agent_starter.cli missing
```

练习 1：给 `Order` 增加 `currency` 字段，并修改模拟后端、摘要和测试。练习 2：模拟上游返回 500 或无效 JSON，检查 CLI 的退出码和错误信息。可以让 AI 帮你写代码，但要自己说明资源关闭、异常映射和数据校验的行为。

## 第 2 周：FastAPI 服务

| 学习时段 | 任务 | 验收 |
| --- | --- | --- |
| 周二 1.5 小时 | 阅读 `api.py` 的路由、依赖注入与 `lifespan` | 能说明 HTTP 客户端何时创建和关闭 |
| 周四 1.5 小时 | 启动 API，调用摘要与 SSE 接口 | 401、200、404、502 四种情况能复现 |
| 周末 4～6 小时 | 完成练习 3、4，补充接口测试 | 流式接口能逐条输出事件，错误不会泄露内部异常 |

保持模拟后端运行，再开一个 PowerShell 窗口：

```powershell
.\.venv\Scripts\python.exe -m uvicorn agent_starter.api:app --port 8000
```

访问 `http://127.0.0.1:8000/docs` 查看接口文档。PowerShell 调用示例：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/orders/A1001/summary -Headers @{ 'X-API-Key' = 'dev-token' }
curl.exe -N -H "X-API-Key: dev-token" http://127.0.0.1:8000/orders/A1001/stream
```

练习 3：增加 `GET /orders/{order_id}`，直接返回经过校验的订单对象。练习 4：把流式输出改成你希望数字员工展示的字段，并增加上游超时的接口测试。最后用 `.\.venv\Scripts\python.exe -m pytest -q` 回归。

完成标准：你能独立修改一个字段、增加一个路由、处理上游故障，解释 Python 异步与 FastAPI 生命周期。

## 第 3～6 周

后四周围绕同一个订单数字员工继续开发：第 3～4 周学习 LangGraph 的状态、节点、条件路由、持久化和人工确认；第 5～6 周完成 FastAPI 部署、SSE、Docker、日志、超时重试和故障演练。

详细的逐日安排、代码阅读顺序和验收命令见 [`WEEKS_3_6.md`](WEEKS_3_6.md)。先重新安装一次依赖：

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
```
