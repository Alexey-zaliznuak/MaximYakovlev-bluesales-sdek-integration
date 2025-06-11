from .order import Order


class GetOrdersResponse:
    def __init__(self, response: dict):
        self.count: int = response['count']
        self.not_returned_count: int = response['notReturnedCount']
        self.orders: list[Order] = [Order(obj) for obj in response['orders']]
        self.payload = response['orders']

    def __repr__(self):
        return str(self.payload)
