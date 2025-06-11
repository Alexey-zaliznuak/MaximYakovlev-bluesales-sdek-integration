from typing import List, Optional

from pydantic import BaseModel

from external.bluesales.managers import Manager


class Country(BaseModel):
    id: int
    name: str

    class Config:
        extra = 'ignore'

class City(BaseModel):
    id: int
    name: str

    class Config:
        extra = 'ignore'

class CRMStatus(BaseModel):
    id: int
    name: str
    color: str
    type: int

    class Config:
        extra = 'ignore'

class Tag(BaseModel):
    id: int
    name: str
    color: str
    textColor: str

    class Config:
        extra = 'ignore'

class Customer(BaseModel):
    id: int
    fullName: str
    photoUrl: str
    country: Optional[Country]
    city: Optional[City]
    birthday: Optional[str]
    sex: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    otherContacts: Optional[str]
    crmStatus: Optional[CRMStatus]
    tags: List[Tag]
    firstContactDate: Optional[str]
    lastContactDate: Optional[str]
    nextContactDate: Optional[str]
    source: Optional[dict]
    manager: Optional[Manager]
    customFields: List[dict]

    class Config:
        extra = 'ignore'
