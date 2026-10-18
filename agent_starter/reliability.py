import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar


T = TypeVar("T")
logger = logging.getLogger(__name__)


async def call_with_retry(
    operation: Callable[[], Awaitable[T]],
    *,
    attempts: int = 3,
    timeout_seconds: float = 5.0,
    base_delay_seconds: float = 0.1,
) -> T:
    """只重试超时和连接类故障；业务错误应由调用方直接处理。"""
    if attempts < 1:
        raise ValueError("attempts 必须大于等于 1")

    last_error: BaseException | None = None
    for attempt in range(1, attempts + 1):
        try:
            return await asyncio.wait_for(operation(), timeout=timeout_seconds)
        except (TimeoutError, ConnectionError) as exc:
            last_error = exc
            logger.warning("operation_failed", extra={"attempt": attempt, "attempts": attempts})
            if attempt < attempts:
                await asyncio.sleep(base_delay_seconds * (2 ** (attempt - 1)))
    assert last_error is not None
    raise last_error
