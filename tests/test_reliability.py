import asyncio

import pytest

from agent_starter.reliability import call_with_retry


@pytest.mark.asyncio
async def test_retry_recovers_from_connection_error() -> None:
    attempts = 0

    async def operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ConnectionError("temporary")
        return "ok"

    result = await call_with_retry(operation, attempts=3, base_delay_seconds=0)
    assert result == "ok"
    assert attempts == 3


@pytest.mark.asyncio
async def test_timeout_is_bounded() -> None:
    async def slow_operation() -> None:
        await asyncio.sleep(1)

    with pytest.raises(TimeoutError):
        await call_with_retry(slow_operation, attempts=1, timeout_seconds=0.01)
