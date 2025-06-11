from .goods import Goods


class GetGoodsResponse:
    def __init__(self, response: dict):
        self.count: int = response['count']
        self.not_returned_count: int = response['notReturnedCount']
        self.goods: list[Goods] = [Goods(obj) for obj in response['goods']]
        self.payload = response['goods']

    def __repr__(self):
        return str(self.payload)
