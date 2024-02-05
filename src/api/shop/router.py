from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, insert, update, func
from sqlalchemy.orm import selectinload

from src.api.shop.models import ShopOrm
from src.database import get_async_session
from src.auth.auth_backend import fastapi_users
from src.api.map.models import CityOrm, StreetOrm
from src.api.shop.utils import get_truncated_time
from src.api.shop.schemas import (
    CreateShopSchema, UpdateShopSchema, GetShopListSchema, CloseOrOpen
)

router = APIRouter(
    prefix="/shop",
    tags=["shop"],
    dependencies=[
        Depends(fastapi_users.current_user(active=True, verified=True))
    ]
)


@router.post("/create_shop")
async def create_shop(
        shop: CreateShopSchema,
        db_session: AsyncSession = Depends(get_async_session)
):
    async with db_session as conn:
        new_shop_id = await conn.execute(
            insert(
                ShopOrm
            ).returning(
                ShopOrm.id
            ).values(
                name=shop.name,
                city_id=shop.city_id,
                street_id=shop.street_id,
                building=shop.building,
                open_time=get_truncated_time(shop.open_time),
                close_time=get_truncated_time(shop.close_time)
            )
        )

        await conn.commit()
        return {"shop_id": new_shop_id.first()[0]}


@router.put("/edit_shop")
async def edit_shop(
        shop: UpdateShopSchema,
        db_session: AsyncSession = Depends(get_async_session)
):
    async with db_session as conn:
        # Можно достать всю модель
        existing_shop: ShopOrm = await conn.scalar(
            select(ShopOrm).where(ShopOrm.id == shop.id).limit(1)
        )

        if existing_shop is None:
            raise HTTPException(status_code=400, detail="Shop not found")

        # Лучше использовать or, т.к. get может вернуть пустую строку
        # get лучше подойдёт когда в Orm моделе могут быть None значения
        # а в ShopOrm все поля обязательные
        # А вообще, можно было не использовать update(),
        # а просто изменить ORM модель
        await conn.execute(
            update(ShopOrm).values(
                name=shop.name or existing_shop.name,
                city_id=shop.city_id or existing_shop.city_id,
                street_id=shop.street_id or existing_shop.street_id,
                building=shop.building or existing_shop.building,
                open_time=get_truncated_time(shop.open_time or existing_shop.open_time),
                close_time=get_truncated_time(shop.close_time or existing_shop.close_time)
            ).where(ShopOrm.id == shop.id)
        )

        await conn.commit()
        return {"message": "The store has been successfully edited"}


@router.get("/", response_model=GetShopListSchema)
async def get_shop(
        street: list[str] = Query(None),
        city: list[str] = Query(None),
        is_open: CloseOrOpen = Query(None),
        db_session: AsyncSession = Depends(get_async_session)
):
    # Создаём базовый запрос
    base_query = select(
        ShopOrm
    ).options(
        # подгружаем все необходимые отношения
        selectinload(ShopOrm.city),
        selectinload(ShopOrm.street)
    )

    # Если параметр указан - добавляем условие к базовому запросу
    if street:
        base_query = base_query.join(
            StreetOrm, ShopOrm.street
        ).where(
            StreetOrm.name.in_(street)
        )

    if city:
        base_query = base_query.join(
            CityOrm, ShopOrm.city
        ).where(
            CityOrm.name.in_(city)
        )

    if is_open is not None:
        base_query = base_query.where(
            func.current_time().between(
                ShopOrm.open_time, ShopOrm.close_time
            ).is_(bool(is_open))
        )

    async with db_session as conn:
        shops: Sequence[ShopOrm] = (
            await conn.scalars(base_query)
        ).all()

    # Хорошая практика собирать pydantic модели из orm моделей (model_validate)
    # Тогда не придётся мучаться с созданием диктов
    return {
        "shops": [
            {
                'name': shop.name,
                'city_name': shop.city.name,
                'street_name': shop.street.name,
                'building': shop.building,
                'open_time': shop.open_time,
                'close_time': shop.close_time,
            }
            for shop in shops
        ]
    }
