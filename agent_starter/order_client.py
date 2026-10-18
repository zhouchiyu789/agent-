from typing import Literal

import httpx
from pydantic import BaseModel, Field, ValidationError


class Order(BaseModel):
    order_id: str
    customer: str
    status: Literal["created", "paid", "shipped", "cancelled"]
    amount: float = Field(ge=0)
    currency: str = "CNY"


class OrderNotFound(Exception):
    pass


class OrderServiceError(Exception):
    pass


class OrderClient:
    def __init__(self, base_url: str, http_client: httpx.AsyncClient) -> None:
        self.base_url = base_url.rstrip("/")
        self.http_client = http_client

    async def get_order(self, order_id: str) -> Order:
        try:
            response = await self.http_client.get(
                f"{self.base_url}/orders/{order_id}"
            )
            if response.status_code == 404:
                raise OrderNotFound(order_id)
            response.raise_for_status()
            return Order.model_validate(response.json())
        except (httpx.HTTPError, ValueError, ValidationError) as exc:
            raise OrderServiceError("订单服务不可用或返回了无效数据") from exc
