# Python 前三天复习题

这份文档只复习前三天已经学过的内容：

- 第一天：变量、字典、条件、函数、返回值和字符串格式化。
- 第二天：类、对象、`self`、模块、异常、`with` 和资源释放。
- 第三天：`async/await`、事件循环、并发、超时和基础异步测试。

建议先只看“问题”，在纸上或编辑器中写出答案，再向下滚动查看“答案”。

---

## 第一部分：项目调用链

前三天需要掌握的订单查询链路是：

```text
main()
→ asyncio.run(show_order())
→ await client.get_order(order_id)
→ await http_client.get(url)
→ 得到 HTTP response
→ 返回 Order 或抛出异常
→ CLI 打印结果或错误
```

这条链路暂时不包含 FastAPI、Pydantic、LangGraph。它们属于后面的学习内容。

---

## 第二部分：问题区

### A. 第一天：普通语法

1. Python 为什么使用缩进表示代码块？
2. `dict` 是什么？下面两个写法有什么区别？

   ```python
   orders[order_id]
   orders.get(order_id)
   ```

3. `if order_id in orders:` 在判断什么？
4. `return` 的作用是什么？
5. 下面函数的参数和返回值分别是什么？

   ```python
   def find_order(order_id: str) -> str:
       return f"订单：{order_id}"
   ```

6. `f"订单 {order_id}"` 中的 `f` 有什么作用？
7. `function` 和 `function()` 有什么区别？
8. `None` 表示什么？下面判断为什么这样写？

   ```python
   if order is None:
       ...
   ```

9. `if __name__ == "__main__":` 的作用是什么？
10. 写一个函数：订单金额大于等于 100 时返回 `True`，否则返回 `False`。

### B. 第二天：类、模块和异常

11. `class Order:` 定义的是什么？
12. `self` 是什么？它对应 Java 中的什么概念？
13. `__init__` 什么时候执行？
14. 下面两行分别做了什么？

   ```python
   order = Order("A1001", "张三", 199.0)
   print(order.summary())
   ```

15. `self.order_id = order_id` 左右两边的 `order_id` 分别是什么？
16. `@dataclass` 的作用是什么？`frozen=True` 表示什么？
17. `import httpx` 和 `from pydantic import BaseModel` 有什么区别？
18. 自定义异常为什么可以这样写？

   ```python
   class OrderNotFound(Exception):
       pass
   ```

19. `raise OrderNotFound(order_id)` 做了什么？
20. `try/except` 的执行流程是什么？
21. `raise NewError(...) from exc` 中的 `from exc` 有什么作用？
22. `with` 代码块解决什么问题？
23. 谁负责关闭当前项目里的 `AsyncClient`？
24. 为什么 `OrderClient` 不应该关闭外部传入的 `AsyncClient`？

### C. 第三天：异步和测试

25. `async def` 定义的是什么？
26. 为什么调用 `load_order()` 后还没有得到最终结果？
27. `await load_order()` 和 `load_order()` 有什么区别？
28. `asyncio.run(main())` 的作用是什么？
29. `await` 网络请求时，事件循环可以做什么？
30. 为什么 `time.sleep()` 不应该放在异步请求链路中？
31. `asyncio.sleep()` 和 `time.sleep()` 的区别是什么？
32. 哪些订单查询适合放进 `asyncio.gather()`？
33. `asyncio.wait_for()` 解决什么问题？
34. 下面表达式的等待时间依次是多少？

   ```python
   0.1 * (2 ** (attempt - 1))
   ```

   当 `attempt` 为 1、2、3 时分别计算。

35. `async with httpx.AsyncClient() as client:` 解决什么问题？
36. `@pytest.mark.asyncio` 的作用是什么？
37. `assert order.amount == 199.0` 在测试什么？
38. `pytest.raises(OrderNotFound)` 在测试什么？
39. `httpx.MockTransport` 为什么适合单元测试？
40. 第三天的订单查询异步调用链是什么？

---

## 第三部分：练习题

### 练习 1：普通函数和字典

写一个函数：

```python
def find_order(order_id: str) -> str:
    ...
```

要求：

- `A1001` 返回一段订单信息。
- 其他订单号返回“订单不存在”。
- 使用字典保存订单。

### 练习 2：类和异常

定义一个 `Order` 类，包含：

```text
order_id
customer
amount
```

再定义 `OrderNotFound`，查询不存在订单时抛出它，并在 `main()` 中捕获。

### 练习 3：异步查询

写一个异步函数：

```python
async def load_order(order_id: str) -> str:
    ...
```

要求：

- 使用 `await asyncio.sleep(0.2)` 模拟网络等待。
- 返回订单查询结果。
- 使用 `asyncio.run(main())` 启动。

### 练习 4：并发和超时

- 用 `asyncio.gather()` 同时查询 `A1001`、`A1002`、`A1003`。
- 用 `asyncio.wait_for()` 限制慢任务最多等待 0.1 秒。
- 分别观察成功和超时的结果。

### 练习 5：异步测试

给一个异步订单函数写测试，至少包含：

- 成功返回结果。
- 不存在订单时抛出 `OrderNotFound`。
- 使用 `pytest.raises` 验证异常。

---

## 第四部分：答案区（问题和答案对照）

下面每一项都重复问题原文，方便你直接对照，不需要来回翻到前面的“问题区”。

### A. 第一天答案

1. **问题：Python 为什么使用缩进表示代码块？**  
   **答案：** Python 用缩进表示代码块，缩进决定哪些语句属于 `if`、函数或循环。通常使用 4 个空格。
2. **问题：`orders[order_id]` 和 `orders.get(order_id)` 有什么区别？**  
   **答案：** `dict` 是键值对集合。`orders[order_id]` 找不到键时抛出 `KeyError`；`orders.get(order_id)` 找不到时返回 `None`，也可以传默认值。
3. **问题：`if order_id in orders:` 在判断什么？**  
   **答案：** 判断 `order_id` 是否是字典中的键。
4. **问题：`return` 的作用是什么？**  
   **答案：** 立即结束当前函数，并把结果交给调用方。
5. **问题：`def find_order(order_id: str) -> str` 的参数和返回值是什么？**  
   **答案：** 参数是 `order_id`，希望是字符串；返回值希望是字符串。
6. **问题：f-string 中的 `f` 有什么作用？**  
   **答案：** `f` 表示 f-string，允许在字符串中使用 `{变量}` 插入值，也可以格式化数字。
7. **问题：`function` 和 `function()` 有什么区别？**  
   **答案：** `function` 是函数本身；`function()` 是调用函数并得到结果。
8. **问题：`None` 表示什么？为什么写 `is None`？**  
   **答案：** `None` 表示没有值。`is None` 是判断对象是否为空值的常用写法。
9. **问题：`if __name__ == "__main__":` 的作用是什么？**  
   **答案：** 只有直接运行这个模块时才执行下面的代码；被其他模块导入时不会自动执行。
10. **问题：如何判断订单金额是否大于等于 100？**  
   **答案：**

   ```python
   def is_large_order(amount: float) -> bool:
       return amount >= 100
   ```

### B. 第二天答案

11. **问题：`class Order:` 定义的是什么？**  **答案：** 定义一个订单对象的结构和行为。
12. **问题：`self` 是什么？**  **答案：** `self` 表示当前对象本身，对应 Java 的 `this`。
13. **问题：`__init__` 什么时候执行？**  **答案：** 创建对象时自动执行，用来初始化对象字段。
14. **问题：`order = Order(...)` 和 `order.summary()` 分别做什么？**  **答案：** 第一行创建 `Order` 对象；第二行调用对象方法并打印返回值。
15. **问题：`self.order_id = order_id` 左右两边分别是什么？**  **答案：** 左边是当前对象的字段，右边是传入构造方法的参数。
16. **问题：`@dataclass` 和 `frozen=True` 的作用是什么？**  **答案：** `@dataclass` 自动生成构造方法等常用代码；`frozen=True` 表示对象创建后字段不能修改。
17. **问题：`import httpx` 和 `from pydantic import BaseModel` 有什么区别？**  **答案：** 前者导入模块名称；后者直接从模块中导入指定名称。
18. **问题：为什么可以定义 `class OrderNotFound(Exception): pass`？**  **答案：** 它定义一个继承自 `Exception` 的业务异常类；`pass` 表示暂时没有额外实现。
19. **问题：`raise OrderNotFound(order_id)` 做了什么？**  **答案：** 主动抛出一个 `OrderNotFound` 异常，并把订单号作为异常信息。
20. **问题：`try/except` 的执行流程是什么？**  **答案：** 先执行 `try`；出现匹配异常后跳到对应 `except`；没有异常则跳过 `except`。
21. **问题：`raise NewError(...) from exc` 中的 `from exc` 有什么作用？**  **答案：** 创建统一的新异常，同时保留底层异常作为异常链，方便日志排查根因。
22. **问题：`with` 代码块解决什么问题？**  **答案：** 自动管理资源的创建和释放，离开代码块时执行清理。
23. **问题：谁负责关闭当前项目里的 `AsyncClient`？**  **答案：** CLI 中由 `show_order()` 的 `async with` 负责；服务中由 FastAPI 的 `lifespan` 负责；测试中由测试自己的 `async with` 负责。
24. **问题：为什么 `OrderClient` 不应该关闭外部传入的 `AsyncClient`？**  **答案：** 因为它只是使用者，不拥有这个客户端。创建者可能还要让其他请求继续复用客户端。

### C. 第三天答案

25. **问题：`async def` 定义的是什么？**  **答案：** 定义一个协程函数。
26. **问题：为什么调用 `load_order()` 后还没有得到最终结果？**  **答案：** `load_order()` 只创建协程对象；协程需要被 `await` 或调度后才会运行。
27. **问题：`load_order()` 和 `await load_order()` 有什么区别？**  **答案：** 前者得到协程对象；后者执行并等待它的最终结果。
28. **问题：`asyncio.run(main())` 的作用是什么？**  **答案：** 创建并运行事件循环，从同步代码进入异步程序。
29. **问题：`await` 网络请求时，事件循环可以做什么？**  **答案：** 当前协程暂停等待网络，事件循环可以执行其他已经准备好的协程。
30. **问题：为什么 `time.sleep()` 不应该放在异步请求链路中？**  **答案：** 它会阻塞事件循环所在的线程，让其他协程也无法运行。
31. **问题：`time.sleep()` 和 `asyncio.sleep()` 有什么区别？**  **答案：** 前者阻塞线程；后者只暂停当前协程，并把执行权交还给事件循环。
32. **问题：哪些查询适合放进 `asyncio.gather()`？**  **答案：** 彼此独立、没有先后依赖的读取操作，例如同时查询多个订单、物流和客户信息。
33. **问题：`asyncio.wait_for()` 解决什么问题？**  **答案：** 给异步操作设置最长等待时间，超过时间就抛出 `TimeoutError`。
34. **问题：`0.1 * (2 ** (attempt - 1))` 在 attempt 为 1、2、3 时是多少？**  **答案：** 分别是 `0.1` 秒、`0.2` 秒、`0.4` 秒。
35. **问题：`async with AsyncClient()` 解决什么问题？**  **答案：** 自动管理异步 HTTP 客户端，退出代码块时关闭连接和连接池。
36. **问题：`@pytest.mark.asyncio` 的作用是什么？**  **答案：** 告诉 pytest 这是异步测试，需要为测试提供事件循环。
37. **问题：`assert order.amount == 199.0` 在测试什么？**  **答案：** 验证订单金额是否等于 `199.0`，不相等时测试失败。
38. **问题：`pytest.raises(OrderNotFound)` 在测试什么？**  **答案：** 验证代码块必须抛出 `OrderNotFound`；没有异常或异常类型不匹配时测试失败。
39. **问题：`httpx.MockTransport` 为什么适合单元测试？**  **答案：** 它拦截 HTTP 请求并返回预设响应，不需要启动真实服务器，测试更快且结果稳定。
40. **问题：第三天的订单查询异步调用链是什么？**  **答案：**

   ```text
   main()
   → asyncio.run(show_order())
   → await client.get_order(order_id)
   → await http_client.get(url)
   → 得到 response
   → 返回 Order 或抛出异常
   → CLI 打印结果或错误
   ```

---

## 第五部分：自测评分

把 40 个问题分成三组，每题 1 分：

- 32～40 分：可以继续学习 Pydantic、FastAPI 和 LangGraph。
- 24～31 分：可以继续，但把答错的题做成小练习再复习一次。
- 23 分以下：重新阅读对应章节，并完成第 1～5 个练习。

每次复习不要只看答案。先写出自己的解释，再用答案检查遗漏。对答错的题，马上修改一个项目示例并重新运行，记忆会比重新通读文档更牢。

---

## 第六部分：复习命令

运行第一天到第三天的练习：

```powershell
.\.venv\Scripts\python.exe examples\day1_exercises.py
.\.venv\Scripts\python.exe examples\day2_classes.py
.\.venv\Scripts\python.exe examples\day3_async.py
```

运行前三天相关测试：

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_order_client.py tests\test_reliability.py -vv
```

复习时要能从空文件写出一个最小流程：

```text
字典保存订单
→ 函数查询订单
→ 类保存订单数据
→ 异常表示查询失败
→ async 函数模拟网络请求
→ await 等待结果
→ pytest 验证成功和失败
```
