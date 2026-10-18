from fastapi.testclient import TestClient

from agent_starter.api import create_app
from agent_starter.config import Settings
from agent_starter.order_client import Order, OrderNotFound, OrderServiceError


class FakeOrderClient:
    async def get_order(self, order_id: str) -> Order:
        if order_id == "missing":
            raise OrderNotFound(order_id)
        if order_id == "failed":
            raise OrderServiceError("upstream failed")
        return Order(order_id=order_id, customer="张三", status="paid", amount=199.0)


def test_summary_stream_and_auth() -> None:
    app = create_app(Settings("http://orders.local", "test-token"), FakeOrderClient())
    with TestClient(app) as client:
        assert client.get("/orders/A1001/summary").status_code == 401
        headers = {"X-API-Key": "test-token"}
        response = client.get("/orders/A1001/summary", headers=headers)
        assert response.status_code == 200
        assert "A1001" in response.json()["summary"]
        response = client.get("/orders/A1001", headers=headers)
        assert response.status_code == 200
        assert response.json()["currency"] == "CNY"
        response = client.get("/orders/A1001/stream", headers=headers)
        assert response.status_code == 200
        assert "event: done" in response.text
        assert "A1001" in response.text

        assert client.get("/orders/missing/summary", headers=headers).status_code == 404
        assert client.get("/orders/missing", headers=headers).status_code == 404
        response = client.get("/orders/failed/summary", headers=headers)
        assert response.status_code == 502
        assert "upstream failed" not in response.text
