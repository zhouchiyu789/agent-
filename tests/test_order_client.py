import httpx
import pytest
from pydantic import ValidationError

from agent_starter.order_client import Order, OrderClient, OrderNotFound, OrderServiceError


@pytest.mark.asyncio
async def test_get_order() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={
        "order_id": "A1001", "customer": "张三", "status": "paid", "amount": 199.0
    }))
    async with httpx.AsyncClient(transport=transport) as http_client:
        order = await OrderClient("http://orders.local", http_client).get_order("A1001")
    assert order.order_id == "A1001"
    assert order.amount == 199.0
    assert order.currency == "CNY"


def test_order_rejects_invalid_fields() -> None:
    with pytest.raises(ValidationError):
        Order(order_id="A1001", customer="张三", status="paid", amount=-1)

    with pytest.raises(ValidationError):
        Order(order_id="A1001", customer="张三", status="unknown", amount=1)

    with pytest.raises(ValidationError):
        Order(order_id="A1001", customer="张三", status="paid")


@pytest.mark.asyncio
async def test_missing_order() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(404))
    async with httpx.AsyncClient(transport=transport) as http_client:
        with pytest.raises(OrderNotFound):
            await OrderClient("http://orders.local", http_client).get_order("missing")


@pytest.mark.asyncio
async def test_invalid_backend_data() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"order_id": "A1001"}))
    async with httpx.AsyncClient(transport=transport) as http_client:
        with pytest.raises(OrderServiceError):
            await OrderClient("http://orders.local", http_client).get_order("A1001")
