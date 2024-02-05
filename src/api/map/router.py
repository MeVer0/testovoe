# Неиспользуемые + смешанные импорты
from sqlalchemy import select, and_
from fastapi import APIRouter, Depends, HTTPException

from src.database import get_async_session
from src.auth.auth_backend import fastapi_users
from src.api.map.models import CityOrm, StreetOrm
from src.api.map.schemas import CitySchema, CityListSchema, StreetListSchema

router = APIRouter(
    prefix="/city",
    tags=["map"],
    dependencies=[
        Depends(fastapi_users.current_user(active=True, verified=True))
    ]
)


# Открывать сессию на каждый запрос не очень хорошая идея
# Так как у постгреса, например, максимальное количество подключений - 100(+15)
# К тому же создание подключения - это дополнительное время
# Хорошее решение в таком случае - какой-то Singleton для объекта сессии, чтобы
# она создавалась один раз при старте апи или при первом запросе

@router.get("/", response_model=CityListSchema)
async def get_all_city(db_session=Depends(get_async_session)):
    async with db_session as conn:
        # select_from обычно используют в исключительных случаях,
        # для обычного селекта в ORM подходе он не нужен
        # Для удобства лучше тайпить не очевидные переменные
        cities: list[tuple[int, int, str]] = await conn.execute(
            select(
                CityOrm.id, CityOrm.region_id, CityOrm.name
            ).order_by(CityOrm.name)
        ).all()

        # try/except здесь не нужен, особенно с Exception, потому что им ты
        # перекроешь все остальные возможные ошибки (ошибки валидации и т.д.)
        # Можно сделать через if, хотя и это не обязательно, так как,
        # в случае отстутсвия городов, правильнее было бы вернуть
        # просто пустой список в моделе
        if not cities:
            raise HTTPException(status_code=400, detail="Cities not found")

        # Переопределять тип переменной не хорошо
        json_field = ("id", "region_id", "name")
        return {
            "cities": [dict(zip(json_field, city)) for city in cities]
        }


@router.get("/{city_id}", response_model=CitySchema)
async def get_city_by_id(city_id: int, db_session=Depends(get_async_session)):
    async with db_session as conn:
        # limit(1) для скорости запроса
        city: tuple[int, str, int] = await conn.execute(
            select(
                CityOrm.id, CityOrm.name, CityOrm.region_id
            ).where(CityOrm.id == city_id).limit(1)
        ).first()

        # Лучше использовать pydantic модели
        # p.s. но я не буду везде это исправлять)
        json_field = ("id", "name", "region_id")
        return dict(zip(json_field, city))


@router.get("/{city_id}/streets", response_model=StreetListSchema)
async def get_streets_by_city_id(
        city_id: int,
        db_session=Depends(get_async_session)
):
    async with db_session as conn:
        streets: list[tuple[int, int, str]] = await conn.execute(
            select(
                StreetOrm.id,
                StreetOrm.city_id,
                StreetOrm.name
            ).join(
                StreetOrm,
                and_(StreetOrm.city_id == CityOrm.id, CityOrm.id == city_id)
            ).order_by(CityOrm.name)
        ).all()

        json_field = ("id", "city_id", "name")
        return {
            "streets": [dict(zip(json_field, street)) for street in streets]
        }
