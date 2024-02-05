from pydantic import BaseModel


# Более современным считается синтаксис тайпинга с |
class CitySchema(BaseModel):
    id: int | None = None
    region_id: int | None = None
    name: str


class CityListSchema(BaseModel):
    cities: list[CitySchema]


class StreetSchema(BaseModel):
    id: int
    city_id: int
    name: str


class StreetListSchema(BaseModel):
    streets: list[StreetSchema]


