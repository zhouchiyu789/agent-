import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from agent_starter.approval_workflow import build_cancel_graph
from agent_starter.order_client import Order
from agent_starter.workflow import build_support_graph


class FakeOrders:
    async def get_order(self, order_id: str) -> Order:
        return Order(order_id=order_id, customer="张三", status="paid", amount=199.0)


class ComplaintRouter:
    async def route(self, query: str) -> str:
        return "complaint"


class FakeCanceller:
    def __init__(self) -> None:
        self.calls = 0

    async def cancel_order(self, order_id: str, reason: str) -> str:
        self.calls += 1
        return f"订单 {order_id} 已取消：{reason}"


@pytest.mark.asyncio
async def test_support_graph_routes_to_order_tool() -> None:
    graph = build_support_graph(FakeOrders(), checkpointer=InMemorySaver())
    result = await graph.ainvoke(
        {"query": "帮我查 A1001", "events": []},
        config={"configurable": {"thread_id": "query-1"}},
    )
    assert "A1001" in result["answer"]
    assert result["events"] == ["route:order_query", "tool:get_order:ok"]


@pytest.mark.asyncio
async def test_support_graph_answers_complaint() -> None:
    graph = build_support_graph(FakeOrders(), router=ComplaintRouter())
    result = await graph.ainvoke({"query": "我不满意", "events": []})
    assert result["answer"] == "已收到您的反馈，我们会尽快处理。"
    assert result["events"] == ["route:complaint", "answer:complaint"]


@pytest.mark.asyncio
async def test_cancel_requires_approval_before_side_effect() -> None:
    canceller = FakeCanceller()
    graph = build_cancel_graph(canceller)
    config = {"configurable": {"thread_id": "cancel-1"}}

    paused = await graph.ainvoke({"order_id": "A1001", "reason": "重复下单"}, config=config)
    assert "__interrupt__" in paused
    assert canceller.calls == 0

    finished = await graph.ainvoke(Command(resume=True), config=config)
    assert finished["approved"] is True
    assert canceller.calls == 1
    assert "已取消" in finished["result"]


@pytest.mark.asyncio
async def test_cancel_rejection_does_not_call_side_effect() -> None:
    canceller = FakeCanceller()
    graph = build_cancel_graph(canceller)
    config = {"configurable": {"thread_id": "cancel-reject-1"}}

    paused = await graph.ainvoke({"order_id": "A1001", "reason": "误操作"}, config=config)
    assert "__interrupt__" in paused

    finished = await graph.ainvoke(Command(resume=False), config=config)
    assert finished["approved"] is False
    assert finished["result"] == "用户拒绝，本次操作未执行。"
    assert canceller.calls == 0
