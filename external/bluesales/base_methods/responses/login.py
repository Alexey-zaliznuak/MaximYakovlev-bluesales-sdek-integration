from pydantic import BaseModel, HttpUrl
from typing import List, Optional

from pydantic import BaseModel, HttpUrl
from typing import List, Optional


class Phrase(BaseModel):
    type: int
    view: str
    text: str
    shortcut: str

    class Config:
        extra = 'ignore'


class Warehouse(BaseModel):
    id: int
    name: str

    class Config:
        extra = 'ignore'


class CrmSource(BaseModel):
    id: int
    name: str

    class Config:
        extra = 'ignore'


class Good(BaseModel):
    id: int
    marking: str
    name: str
    price: float
    page: str
    sizes: List[str]
    description: Optional[str]
    shopPageLink: Optional[str]
    weight: Optional[float] = None
    isArchived: bool

    class Config:
        extra = 'ignore'


class User(BaseModel):
    id: int
    name: str
    fmlName: str
    color: str
    textColor: str

    class Config:
        extra = 'ignore'


class CdekTariff(BaseModel):
    tariffCode: int
    name: str
    mode: int

    class Config:
        extra = 'ignore'


class CrmStatus(BaseModel):
    id: int
    name: str

    class Config:
        extra = 'ignore'


class OrderStatus(BaseModel):
    id: int
    name: str

    class Config:
        extra = 'ignore'


class Tag(BaseModel):
    id: int
    name: str
    color: str
    textColor: str

    class Config:
        extra = 'ignore'


class VkGroup(BaseModel):
    id: str
    screenName: str
    name: str

    class Config:
        extra = 'ignore'


class VkGroupSetting(BaseModel):
    vkGroup: VkGroup
    vkGroupAccessToken: str

    class Config:
        extra = 'ignore'


class AdditionalSettings(BaseModel):
    vkGroupsSettings: List[VkGroupSetting]

    class Config:
        extra = 'ignore'


class ShopSettings(BaseModel):
    additionalSettings: AdditionalSettings

    class Config:
        extra = 'ignore'


class LoginData(BaseModel):
    allPhrases: List[Phrase]
    allWarehouses: List[Warehouse]
    allCrmSources: List[CrmSource]
    allGoods: List[Good]
    allUsers: List[User]
    allCdekTariffs: List[CdekTariff]
    allCrmStatuses: List[CrmStatus]
    allOrderStatuses: List[OrderStatus]
    allTags: List[Tag]
    shopSettings: ShopSettings

    class Config:
        extra = 'ignore'
