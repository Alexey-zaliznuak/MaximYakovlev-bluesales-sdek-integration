import hashlib
import logging
from functools import cached_property

from external.bluesales.base_methods.responses.login import LoginData

from .base_methods import BaseMethodsService
from .customers import CustomersService
from .goods import GoodsService
from .orders import OrdersService
from .request_api import RequestApi
from .managers import ManagersService

logger = logging.getLogger(__name__)


def get_hash(password):
    return hashlib.md5(bytearray(password, 'utf-8')).hexdigest().upper()


class BlueSalesService:
    def __init__(self, login: str, password: str, *, load_login_data_on_init: bool = False):
        self.login: str = login
        self.__password: str = get_hash(password)
        self._rq = RequestApi(self.login, self.__password)

        self.base_methods = BaseMethodsService(self._rq)

        self.customers = CustomersService(self._rq)
        self.orders = OrdersService(self._rq)
        self.goods = GoodsService(self._rq)
        self.managers = ManagersService(self._rq)

        if load_login_data_on_init:
            self.login_data

    @cached_property
    def login_data(self) -> LoginData:
        return self.base_methods.login_data
