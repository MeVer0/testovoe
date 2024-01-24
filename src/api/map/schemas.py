from typing import List, Optional

from pydantic import BaseModel


class CitySchema(BaseModel):

    id: Optional[int] = None
    region_id: Optional[int] = None
    name: str


class CityListSchema(BaseModel):

    cities: list[CitySchema]


class StreetSchema(BaseModel):

    id: int
    city_id: int
    name: str


class StreetListSchema(BaseModel):

    streets: list[StreetSchema]


