from external.bluesales.api_methods import GoodsMethods
from external.bluesales.request_api import RequestApi

from .get_response import GetGoodsResponse
from .goods import Goods
from .utils import GoodsUtils


class GoodsService:
    def __init__(self, request_api: RequestApi):
        self.request_api = request_api
        self.utils = GoodsUtils()

    def get_all(
        self,
        pageSize: int = 500
    ) -> list[Goods]:

        data = {
            "startRowNumber": 0,
            "pageSize": pageSize
        }

        response = self.request_api.send(
            GoodsMethods.get,
            data=data
        )

        return [Goods(goods) for goods in response["goods"]]
