"""第三天练习：async/await、并发、超时和异步资源管理。"""

import asyncio
import time


async def load_order(order_id: str) -> str:
    print(f"开始查询 {order_id}")
    await asyncio.sleep(0.2)
    print(f"查询完成 {order_id}")
    return f"订单 {order_id}：查询成功"


async def exercise_one() -> None:
    print("练习 1：单个异步任务")
    result = await load_order("A1001")
    print(result)


async def exercise_two() -> None:
    print("\n练习 2：并发查询三个订单")
    started = time.perf_counter()
    first, second, third = await asyncio.gather(
        load_order("A1001"),
        load_order("A1002"),
        load_order("A1003"),
    )
    print(first)
    print(second)
    print(third)
    print(f"并发耗时：{time.perf_counter() - started:.3f} 秒")

    print("练习 2b：顺序查询两个订单")
    started = time.perf_counter()
    await load_order("A1001")
    await load_order("A1002")
    print(f"顺序耗时：{time.perf_counter() - started:.3f} 秒")


async def slow_operation() -> str:
    await asyncio.sleep(1)
    return "慢任务完成"


async def exercise_three() -> None:
    print("\n练习 3：超时控制")
    try:
        result = await asyncio.wait_for(slow_operation(), timeout=0.1)
        print(result)
    except TimeoutError:
        print("任务超时，已停止等待")


async def main() -> None:
    await exercise_one()
    await exercise_two()
    await exercise_three()


if __name__ == "__main__":
    asyncio.run(main())
