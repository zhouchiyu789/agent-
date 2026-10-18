import asyncio
import hmac
import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import StreamingResponse

from agent_starter.config import Settings
from agent_starter.order_client import Order, OrderClient, OrderNotFound, OrderServiceError

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None, order_client: OrderClient | None = None) -> FastAPI:
    settings = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if order_client is not None:
            app.state.order_client = order_client
            yield
        else:
            async with httpx.AsyncClient(timeout=5.0) as http_client:
                app.state.order_client = OrderClient(settings.order_api_url, http_client)
                yield

    app = FastAPI(title="Python Agent 学习服务", lifespan=lifespan)

    async def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
        if x_api_key is None or not hmac.compare_digest(x_api_key, settings.api_key):
            raise HTTPException(status_code=401, detail="无效的 API Key")

    def get_client(request: Request) -> OrderClient:
        return request.app.state.order_client

    async def load_order(order_id: str, client: OrderClient) -> Order:
        try:
            return await client.get_order(order_id)
        except OrderNotFound as exc:
            raise HTTPException(status_code=404, detail="订单不存在") from exc
        except OrderServiceError as exc:
            logger.exception("查询订单失败: %s", order_id)
            raise HTTPException(status_code=502, detail="订单服务暂时不可用") from exc

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/orders/{order_id}/summary", dependencies=[Depends(require_api_key)])
    async def order_summary(order_id: str, client: OrderClient = Depends(get_client)) -> dict[str, str]:
        order = await load_order(order_id, client)
        return {"summary": f"订单 {order.order_id}，客户 {order.customer}，状态 {order.status}，金额 {order.amount:.2f} 元。"}

    @app.get("/orders/{order_id}", response_model=Order, dependencies=[Depends(require_api_key)])
    async def get_order(order_id: str, client: OrderClient = Depends(get_client)) -> Order:
        return await load_order(order_id, client)

    @app.get("/orders/{order_id}/stream", dependencies=[Depends(require_api_key)])
    async def stream_order_summary(
        order_id: str, request: Request, client: OrderClient = Depends(get_client)
    ) -> StreamingResponse:
        order = await load_order(order_id, client)

        async def events() -> AsyncIterator[str]:
            chunks = [f"订单 {order.order_id}", f"，客户 {order.customer}", f"，状态 {order.status}", f"，金额 {order.amount:.2f} 元。"]
            for chunk in chunks:
                if await request.is_disconnected():
                    return
                yield f"event: message\ndata: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0)
            yield "event: done\ndata: {}\n\n"

        return StreamingResponse(events(), media_type="text/event-stream")

    return app


app = create_app()
