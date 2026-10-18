from dataclasses import dataclass


class OrderNotFound(Exception):
    pass


@dataclass(frozen=True)
class Order:
    order_id: str
    customer: str
    status: str
    amount: float

    def summary(self) -> str:
        return (
            f"订单 {self.order_id}，"
            f"客户 {self.customer}，"
            f"状态 {self.status}，"
            f"金额 {self.amount:.2f} 元"
        )


orders = {
    "A1001": Order("A1001", "张三", "paid", 199.0),
    "A1002": Order("A1002", "李四", "shipped", 88.5),
}


def find_order(order_id: str) -> Order:
    order = orders.get(order_id)
    if order is None:
        raise OrderNotFound(order_id)
    return order


def main() -> None:
    try:
        print(find_order("A1001").summary())
        print(find_order("missing").summary())
    except OrderNotFound as exc:
        print(f"订单不存在：{exc}")


if __name__ == "__main__":
    main()
