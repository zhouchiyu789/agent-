import hmac
import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel, Field

from agent_starter.config import Settings
from agent_starter.order_client import OrderClient
from agent_starter.workflow import build_support_graph


logger = logging.getLogger(__name__)


class AgentRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    thread_id: str = Field(min_length=1, max_length=100)


def create_agent_app(settings: Settings | None = None, graph: Any | None = None) -> FastAPI:
    settings = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if graph is not None:
            app.state.graph = graph
            yield
            return
        async with httpx.AsyncClient(timeout=settings.upstream_timeout_seconds) as client:
            app.state.graph = build_support_graph(
                OrderClient(settings.order_api_url, client), checkpointer=InMemorySaver()
            )
            yield

    app = FastAPI(title="LangGraph 数字员工", lifespan=lifespan)

    @app.middleware("http")
    async def access_log(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        started = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request_complete",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            },
        )
        return response

    async def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
        if x_api_key is None or not hmac.compare_digest(x_api_key, settings.api_key):
            raise HTTPException(status_code=401, detail="无效的 API Key")

    def get_graph(request: Request):
        return request.app.state.graph

    @app.get("/health/live")
    async def live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready")
    async def ready(request: Request) -> dict[str, str]:
        if not hasattr(request.app.state, "graph"):
            raise HTTPException(status_code=503, detail="工作流尚未初始化")
        return {"status": "ready"}

    @app.post("/agent/invoke", dependencies=[Depends(require_api_key)])
    async def invoke_agent(body: AgentRequest, current_graph=Depends(get_graph)) -> dict[str, Any]:
        config = {"configurable": {"thread_id": body.thread_id}}
        result = await current_graph.ainvoke({"query": body.query, "events": []}, config=config)
        return {"answer": result["answer"], "events": result.get("events", [])}

    @app.post("/agent/stream", dependencies=[Depends(require_api_key)])
    async def stream_agent(body: AgentRequest, current_graph=Depends(get_graph)) -> StreamingResponse:
        config = {"configurable": {"thread_id": body.thread_id}}

        async def event_stream() -> AsyncIterator[str]:
            async for update in current_graph.astream(
                {"query": body.query, "events": []}, config=config, stream_mode="updates"
            ):
                yield f"event: node\ndata: {json.dumps(update, ensure_ascii=False)}\n\n"
            yield "event: done\ndata: {}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    return app


app = create_agent_app()
