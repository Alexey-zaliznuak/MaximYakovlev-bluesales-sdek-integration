# -*- coding: utf-8 -*-
from typing import Optional
from pydantic import BaseModel, Field

from ..api_methods import ManagersMethods
from ..request_api import RequestApi


class Manager(BaseModel):
    id: int
    full_name: str = Field(..., alias="fullName")
    email: str
    login: str
    phone: Optional[str] = ""
    vk: Optional[str] = None
    last_login_date: str = Field(..., alias="lastLoginDate")  # ISO 8601 datetime
    last_activity_date: str = Field(..., alias="lastActivityDate")  # ISO 8601 datetime
    is_active: bool = Field(..., alias="isActive")

    class Meta:
        from_attributes = True


class ManagersService:
    def __init__(self, request_api: RequestApi):
        self.request_api = request_api

    def get_all(self):
        data = self.request_api.send(method=ManagersMethods.get)
        return [Manager(**obj) for obj in data]
