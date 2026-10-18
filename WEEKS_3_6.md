# 第 3～6 周：LangGraph、部署与排错

这四周的目标不是继续堆 Agent 概念，而是把你已经用 Java 做过的数字员工，用 Python 和 LangGraph 重写一条完整链路。每周按周二 1.5 小时、周四 1.5 小时、周末 4～6 小时安排，每周只交付一个可运行成果。

## 使用顺序

先运行完整测试，确认基线：

```powershell
cd 'D:\agent学习'
.\.venv\Scripts\python.exe -m pytest -q
```

相关文件：

- `agent_starter/workflow.py`：查询订单的状态图。
- `agent_starter/approval_workflow.py`：取消订单前暂停并等待人工确认。
- `agent_starter/agent_api.py`：把图暴露为普通接口和 SSE 接口。
- `agent_starter/reliability.py`：超时、重试和退避。
- `tests/test_workflow.py`：路由、工具执行和人工确认测试。
- `tests/test_agent_api.py`：部署接口测试。
- `Dockerfile`、`compose.yaml`：容器部署。

## 第 3 周：理解 LangGraph 的执行模型

本周成果：能画出并运行 `classify → query_order / answer_general → END`，能从日志或状态判断执行了哪个节点。

### 周二，90 分钟

1. 前 15 分钟：运行 `test_support_graph_routes_to_order_tool`，观察输入和最终状态。
2. 中间 50 分钟：阅读 `workflow.py`，重点看 `AgentState`、节点返回的局部状态、条件边和 `compile()`。
3. 后 25 分钟：增加一个 `complaint` 意图，只返回固定回复，先不接模型。

验收：你能解释 LangGraph 的 state 类似什么、节点为什么只返回改动字段、条件边如何决定下一步。

### 周四，90 分钟

1. 前 15 分钟：给普通问题和订单问题各跑一次 `ainvoke()`。
2. 中间 55 分钟：把 `RuleBasedRouter` 替换成你现有模型的结构化输出，返回 `order_query` 或 `general`。
3. 后 20 分钟：补 3 个路由测试，覆盖正常订单号、没有订单号和模型输出异常。

模型调用放在 `IntentRouter.route()` 的实现中，图的其他部分不需要知道你用的模型供应商。

### 周末，4～6 小时

把 `OrderReader` 适配成你已有的 MCP 工具。保持 `get_order(order_id) -> Order` 这个 Python 边界，MCP 会话、参数协议和返回值转换都留在适配器内部。

故意制造三种失败：订单不存在、MCP 超时、MCP 返回字段缺失。最终状态必须分别给出稳定的用户消息，并在 `events` 中留下不同结果。

本周完成标准：你可以不看教程增加一个节点、一个条件分支和一个工具适配器，并能为它写测试。

## 第 4 周：状态持久化与人工确认

本周成果：取消订单图在执行副作用前暂停；同一个 `thread_id` 能恢复，拒绝确认时不会调用工具。

### 周二，90 分钟

1. 前 20 分钟：阅读 `test_cancel_requires_approval_before_side_effect`，先理解调用顺序。
2. 中间 50 分钟：阅读 `approval_workflow.py` 的 `interrupt()`、checkpointer 和 `Command(resume=...)`。
3. 后 20 分钟：分别用 `True`、`False` 恢复工作流，检查工具调用次数。

验收：暂停时 `cancel_order()` 调用次数必须为 0；批准后为 1；拒绝后仍为 0。

### 周四，90 分钟

1. 前 20 分钟：用两个不同的 `thread_id` 同时发起取消，观察状态隔离。
2. 中间 50 分钟：给状态增加 `operator_id` 和 `requested_at`，确认页返回这些字段。
3. 后 20 分钟：补重复恢复测试，设计幂等键 `thread_id + order_id + action`。

`InMemorySaver` 只适合练习和单进程演示。你自己的商用版本应替换为数据库 checkpointer，并让业务接口本身也校验幂等键。

### 周末，4～6 小时

把你现有数字员工的一条真实流程迁入图中，建议选择 3～5 个节点的流程。至少包含：一个模型节点、一个 MCP 工具节点、一个条件分支、一个人工确认点和一个失败出口。

本周完成标准：程序重启后如何恢复、重复点击确认是否重复执行、两个用户是否串状态，这三个问题你都能用代码或设计说明回答。

## 第 5 周：FastAPI 与容器部署

本周成果：工作流可以通过 HTTP 和 SSE 调用，并在 Docker 中运行。

### 周二，90 分钟

1. 前 20 分钟：阅读 `agent_api.py` 的 `lifespan` 和依赖注入。
2. 中间 50 分钟：启动模拟订单服务和 Agent API，调用 `/agent/invoke`。
3. 后 20 分钟：检查 401、422、502 三类错误是否有明确边界。

启动命令：

```powershell
# 终端 1
.\.venv\Scripts\python.exe -m uvicorn agent_starter.mock_backend:app --port 8001

# 终端 2
.\.venv\Scripts\python.exe -m uvicorn agent_starter.agent_api:app --port 8000
```

调用命令：

```powershell
$body = @{ query = '帮我查 A1001'; thread_id = 'demo-1' } | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/agent/invoke -Method Post -ContentType 'application/json' -Headers @{ 'X-API-Key' = 'dev-token' } -Body $body
```

### 周四，90 分钟

1. 前 20 分钟：调用 `/agent/stream`，观察每个节点的 SSE 更新。
2. 中间 50 分钟：增加客户端断开处理和一次并发调用测试。
3. 后 20 分钟：检查 `thread_id` 是否来自可信用户上下文，不能让用户读取别人的状态。

SSE 调用：

```powershell
curl.exe -N -X POST http://127.0.0.1:8000/agent/stream -H "Content-Type: application/json" -H "X-API-Key: dev-token" --data-binary '@examples/agent_request.json'
```

### 周末，4～6 小时

运行容器：

```powershell
docker compose up --build
docker compose ps
```

检查 `/health/live` 和 `/health/ready`。然后停止订单模拟服务，确认 Agent 容器仍存活，但请求会返回可理解的上游故障信息。把镜像启动命令、环境变量和健康检查写进你自己的项目文档。

本周完成标准：在一台新机器上，只依赖 Docker 和环境变量就能启动；密钥不写入镜像；服务收到退出信号时能释放 HTTP/MCP 连接。

## 第 6 周：排错与上线演练

本周成果：能快速判断问题发生在路由、模型、MCP、业务接口还是状态恢复，并证明修复有效。

### 周二，90 分钟

1. 前 20 分钟：阅读 `agent_api.py` 的请求 ID 和耗时日志。
2. 中间 50 分钟：让每个节点记录 `thread_id`、节点名、耗时和结果类型，禁止记录密钥及完整敏感输入。
3. 后 20 分钟：拿一次失败请求，从 API 日志追到具体节点和工具调用。

### 周四，90 分钟

1. 前 20 分钟：阅读 `reliability.py`，运行两个可靠性测试。
2. 中间 50 分钟：分别注入超时、连接失败和业务 400；只重试瞬时故障。
3. 后 20 分钟：确认总超时有上限，重试不会让写操作重复执行。

不要对所有异常统一重试。参数错误、权限错误、余额不足等业务结果重试没有意义；取消订单这类写操作必须配合幂等键。

### 周末，4～6 小时

完成一次故障演练清单：

1. 模型接口超时。
2. MCP 进程退出。
3. 订单接口返回 500 和非法 JSON。
4. 同一确认请求提交两次。
5. 两个用户误用了同一个 `thread_id`。
6. SSE 客户端中途断开。

每个场景记录：预期行为、实际日志、用户看到的信息、是否重试、是否产生副作用。最后运行：

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

本周完成标准：面对一次失败，你能在 10 分钟内定位到层次，给出可复现输入，并用测试证明修复没有造成重复执行。

## 每次学习的固定节奏

周二和周四的 90 分钟固定分配为：10 分钟明确本次验收结果，20 分钟阅读一条完整调用链，45 分钟亲手修改，15 分钟跑测试并写三行笔记。AI 可以生成样板代码，但最后 15 分钟必须由你解释状态变化、异常传播和副作用边界。

周末先用 30 分钟定一个可演示目标，再用 2～3 小时实现，1 小时注入失败，最后 30 分钟整理测试、日志和 README。剩余时间用于把本周代码接入你的真实 MCP 或 Java 服务。

如果某周没有完成，不要同时推进下一周。判断是否可以继续的唯一标准是本周“完成标准”，而不是代码写了多少或视频看了多少。
