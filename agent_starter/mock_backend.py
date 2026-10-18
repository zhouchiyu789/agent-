from fastapi import FastAPI, HTTPException

from agent_starter.order_client import Order

app = FastAPI(title="模拟 Java 订单服务")

ORDERS = {
    "A1001": Order(order_id="A1001", customer="张三", status="paid", amount=199.0, currency="CNY"),
    "A1002": Order(order_id="A1002", customer="李四", status="shipped", amount=88.5, currency="CNY"),
}


@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str) -> Order:
    order = ORDERS.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order
