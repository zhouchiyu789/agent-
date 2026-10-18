from fastapi.testclient import TestClient

from agent_starter.agent_api import create_agent_app
from agent_starter.config import Settings


class FakeGraph:
    async def ainvoke(self, state, config):
        return {"answer": f"收到：{state['query']}", "events": ["fake:ok"]}

    async def astream(self, state, config, stream_mode):
        yield {"classify": {"intent": "general"}}
        yield {"answer_general": {"answer": "完成"}}


def test_deployed_agent_api() -> None:
    settings = Settings("http://orders.local", "test-token")
    app = create_agent_app(settings, FakeGraph())
    with TestClient(app) as client:
        assert client.get("/health/live").status_code == 200
        assert client.get("/health/ready").status_code == 200
        assert client.post("/agent/invoke", json={"query": "hello", "thread_id": "t1"}).status_code == 401

        headers = {"X-API-Key": "test-token"}
        response = client.post(
            "/agent/invoke", json={"query": "hello", "thread_id": "t1"}, headers=headers
        )
        assert response.status_code == 200
        assert response.json()["events"] == ["fake:ok"]

        response = client.post(
            "/agent/stream", json={"query": "hello", "thread_id": "t1"}, headers=headers
        )
        assert response.status_code == 200
        assert "event: done" in response.text
