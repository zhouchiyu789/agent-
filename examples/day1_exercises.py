"""第一天练习：变量、字典、条件、函数和字符串格式化。"""


def find_order(order_id: str) -> str:
    orders = {
        "A1001": "订单 A1001：张三，已支付，199 元",
        "A1002": "订单 A1002：李四，已发货，88.5 元",
        "A1003": "订单 A1003：王五，已创建，50 元",
    }

    if order_id in orders:
        return orders[order_id]

    return f"订单 {order_id} 不存在，请检查订单号"


def is_large_order(amount: float) -> bool:
    return amount >= 100


def order_status_message(status: str) -> str:
    if status == "paid":
        return "订单已经支付"
    if status == "shipped":
        return "订单已经发货"
    if status == "created":
        return "订单已创建，等待支付"
    return f"未知订单状态：{status}"


def main() -> None:
    print("练习 1：查询订单")
    print(find_order("A1001"))
    print(find_order("A1003"))
    print(find_order("A9999"))

    print("\n练习 2：判断金额")
    print(f"199 元是否大订单：{is_large_order(199.0)}")
    print(f"50 元是否大订单：{is_large_order(50.0)}")

    print("\n练习 3：处理订单状态")
    print(order_status_message("paid"))
    print(order_status_message("shipped"))
    print(order_status_message("unknown"))


if __name__ == "__main__":
    main()
