from functools import cached_property

from external.bluesales.api_methods import BaseMethods
from external.bluesales.request_api import RequestApi

from .responses.login import LoginData


class BaseMethodsService:
    def __init__(self, request_api: RequestApi):
        self.request_api = request_api

    @cached_property
    def login_data(self) -> LoginData:
        return LoginData(**self.request_api.send(method=BaseMethods.login))
