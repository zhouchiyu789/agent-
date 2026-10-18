import operator
import re
from typing import Annotated, Literal, Protocol, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from agent_starter.order_client import Order, OrderNotFound, OrderServiceError


Intent = Literal["order_query", "general", "complaint"]


class AgentState(TypedDict, total=False):
    query: str
    intent: Intent
    order_id: str
    answer: str
    events: Annotated[list[str], operator.add]


class IntentRouter(Protocol):
    async def route(self, query: str) -> Intent: ...


class OrderReader(Protocol):
    async def get_order(self, order_id: str) -> Order: ...


class RuleBasedRouter:
    """本地可测试的路由器；第 3 周练习时替换成你的模型结构化输出。"""

    async def route(self, query: str) -> Intent:
        if any(word in query for word in ("投诉", "抱怨", "不满意")):
            return "complaint"
        return "order_query" if re.search(r"[A-Za-z]\d{4,}", query) else "general"


def extract_order_id(query: str) -> str | None:
    match = re.search(r"\b([A-Za-z]\d{4,})\b", query)
    return match.group(1).upper() if match else None


def build_support_graph(
    order_reader: OrderReader,
    router: IntentRouter | None = None,
    checkpointer: InMemorySaver | None = None,
):
    router = router or RuleBasedRouter()

    async def classify(state: AgentState) -> AgentState:
        intent = await router.route(state["query"])
        return {"intent": intent, "events": [f"route:{intent}"]}

    async def query_order(state: AgentState) -> AgentState:
        order_id = extract_order_id(state["query"])
        if order_id is None:
            return {"answer": "请提供订单号，例如 A1001。", "events": ["tool:skipped"]}
        try:
            order = await order_reader.get_order(order_id)
            answer = (
                f"订单 {order.order_id}，客户 {order.customer}，"
                f"状态 {order.status}，金额 {order.amount:.2f} 元。"
            )
            return {"order_id": order_id, "answer": answer, "events": ["tool:get_order:ok"]}
        except OrderNotFound:
            return {"order_id": order_id, "answer": f"没有找到订单 {order_id}。", "events": ["tool:get_order:not_found"]}
        except OrderServiceError:
            return {"order_id": order_id, "answer": "订单服务暂时不可用，请稍后重试。", "events": ["tool:get_order:failed"]}

    async def answer_general(state: AgentState) -> AgentState:
        return {
            "answer": "当前示例只处理订单查询；请接入你的模型或 Skills 生成通用回复。",
            "events": ["answer:general"],
        }

    async def answer_complaint(state: AgentState) -> AgentState:
        return {
            "answer": "已收到您的反馈，我们会尽快处理。",
            "events": ["answer:complaint"],
        }

    builder = StateGraph(AgentState)
    builder.add_node("classify", classify)
    builder.add_node("query_order", query_order)
    builder.add_node("answer_general", answer_general)
    builder.add_node("answer_complaint", answer_complaint)
    builder.add_edge(START, "classify")
    builder.add_conditional_edges(
        "classify",
        lambda state: state["intent"],
        {
            "order_query": "query_order",
            "general": "answer_general",
            "complaint": "answer_complaint",
        },
    )
    builder.add_edge("query_order", END)
    builder.add_edge("answer_general", END)
    builder.add_edge("answer_complaint", END)
    return builder.compile(checkpointer=checkpointer)
