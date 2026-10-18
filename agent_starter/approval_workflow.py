from typing import Protocol, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt


class CancelState(TypedDict, total=False):
    order_id: str
    reason: str
    approved: bool
    result: str


class OrderCanceller(Protocol):
    async def cancel_order(self, order_id: str, reason: str) -> str: ...


def build_cancel_graph(canceller: OrderCanceller, checkpointer: InMemorySaver | None = None):
    async def request_approval(state: CancelState) -> CancelState:
        approved = interrupt(
            {
                "action": "cancel_order",
                "order_id": state["order_id"],
                "reason": state["reason"],
                "message": "确认后才会执行取消操作",
            }
        )
        return {"approved": bool(approved)}

    def after_approval(state: CancelState) -> str:
        return "execute" if state["approved"] else "reject"

    async def execute(state: CancelState) -> CancelState:
        result = await canceller.cancel_order(state["order_id"], state["reason"])
        return {"result": result}

    async def reject(state: CancelState) -> CancelState:
        return {"result": "用户拒绝，本次操作未执行。"}

    builder = StateGraph(CancelState)
    builder.add_node("request_approval", request_approval)
    builder.add_node("execute", execute)
    builder.add_node("reject", reject)
    builder.add_edge(START, "request_approval")
    builder.add_conditional_edges(
        "request_approval", after_approval, {"execute": "execute", "reject": "reject"}
    )
    builder.add_edge("execute", END)
    builder.add_edge("reject", END)
    return builder.compile(checkpointer=checkpointer or InMemorySaver())
