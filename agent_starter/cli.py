import argparse
import asyncio
import logging

import httpx

from agent_starter.config import Settings
from agent_starter.order_client import OrderClient, OrderNotFound, OrderServiceError


async def show_order(order_id: str) -> None:
    settings = Settings.from_env()
    async with httpx.AsyncClient(timeout=5.0) as http_client:
        client = OrderClient(settings.order_api_url, http_client)
        order = await client.get_order(order_id)
        print(order.model_dump_json(indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="查询模拟订单服务")
    parser.add_argument("order_id", help="例如 A1001")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(show_order(args.order_id))
    except OrderNotFound:
        parser.exit(1, f"订单不存在: {args.order_id}\n")
    except OrderServiceError as exc:
        parser.exit(2, f"查询失败: {exc}\n")


if __name__ == "__main__":
    main()
