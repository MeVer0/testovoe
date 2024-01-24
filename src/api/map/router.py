from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_
from src.auth.auth_backend import fastapi_users

from src.database import get_async_session


from src.api.map.schemas import CitySchema, CityListSchema, StreetSchema, StreetListSchema
from src.api.map.models import CityOrm, StreetOrm


router = APIRouter(
    prefix="/city",
    tags=["map"],
    dependencies=[Depends(fastapi_users.current_user(active=True, verified=True))]
)


@router.get("", response_model=CityListSchema)
async def get_all_city(db_session=Depends(get_async_session)):

    async with db_session as conn:
        try:
            cities = await conn.execute(
                select(CityOrm.id,
                       CityOrm.region_id,
                       CityOrm.name
                       ).select_from(CityOrm).order_by(CityOrm.name)
            )

            json_field = ("id", "region_id", "name")
            cities = {"cities": [dict(zip(json_field, city)) for city in cities.all()]}
            return cities

        except Exception:
            raise HTTPException(status_code=400, detail="Cities not found")


@router.get("/{city_id}", response_model=CitySchema)
async def get_city_by_id(city_id: int, db_session=Depends(get_async_session)):

    async with db_session as conn:
        try:
            city = await conn.execute(
                select(CityOrm.id, CityOrm.name, CityOrm.region_id)
                .select_from(CityOrm)
                .where(CityOrm.id == city_id)
            )

            json_field = ("id", "name", "region_id")
            city = dict(zip(json_field, city.first()))
            return city
        except Exception as r:
            raise HTTPException(status_code=400, detail="City not found")


@router.get("/{city_id}/streets", response_model=StreetListSchema)
async def get_streets_by_city_id(city_id: int, db_session=Depends(get_async_session)):

    async with db_session as conn:
        try:
            streets = await conn.execute(
                select(StreetOrm.id,
                       StreetOrm.city_id,
                       StreetOrm.name)
                .select_from(CityOrm)
                .join(StreetOrm, and_(StreetOrm.city_id == CityOrm.id, CityOrm.id == city_id)).order_by(CityOrm.name)
            )

            json_field = ("id", "city_id", "name")
            streets = {"streets": [dict(zip(json_field, street)) for street in streets.all()]}
            return streets
        except Exception:
            raise HTTPException(status_code=400, detail="City not found")
