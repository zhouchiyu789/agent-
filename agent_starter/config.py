import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    order_api_url: str
    api_key: str
    upstream_timeout_seconds: float = 5.0

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            order_api_url=os.getenv("ORDER_API_URL", "http://127.0.0.1:8001"),
            api_key=os.getenv("APP_API_KEY", "dev-token"),
            upstream_timeout_seconds=float(os.getenv("UPSTREAM_TIMEOUT_SECONDS", "5")),
        )
