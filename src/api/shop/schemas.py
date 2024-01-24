import datetime
from enum import IntEnum
from typing import Optional

from pydantic import BaseModel


class CreateShopSchema(BaseModel):
    name: str
    city_id: int
    street_id: int
    building: str
    open_time: datetime.time
    close_time: datetime.time


class GetShopSchema(BaseModel):

    name: str
    city_name: str
    street_name: str
    open_time: datetime.time
    close_time: datetime.time


class GetShopListSchema(BaseModel):
    shops: list[GetShopSchema]

# class GetShopSchemaCity(BaseModel):
#     city_id: int
#     name: str
#
#
# class GetShopSchemaStreet(BaseModel):
#     street_id: int
#     name: str
#
#


class UpdateShopSchema(BaseModel):
    id: int
    name: Optional[str] = None
    city_id: Optional[int] = None
    street_id: Optional[int] = None
    building: Optional[str] = None
    open_time: Optional[datetime.time] = None
    close_time: Optional[datetime.time] = None


class CloseOrOpen(IntEnum):
    open = 1
    close = 0
