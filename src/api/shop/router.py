import time
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_, insert, update, case, or_, func, not_

from src.api.map.models import CityOrm, StreetOrm
from src.auth.auth_backend import fastapi_users

from src.database import get_async_session


from src.api.shop.schemas import CreateShopSchema, UpdateShopSchema, GetShopListSchema, CloseOrOpen
from src.api.shop.models import ShopOrm

from src.api.shop.utils import get_truncated_time

router = APIRouter(
    prefix="/shop",
    tags=["shop"],
    dependencies=[Depends(fastapi_users.current_user(active=True, verified=True))]
)


@router.post("/create_shop")
async def create_shop(
        shop: CreateShopSchema,
        db_session=Depends(get_async_session),):

    async with db_session as conn:
        try:
            new_shop_id = await conn.execute(
               insert(ShopOrm).returning(ShopOrm.id).values(name=shop.name,
                                                            city_id=shop.city_id,
                                                            street_id=shop.street_id,
                                                            building=shop.building,
                                                            open_time=await get_truncated_time(shop.open_time),
                                                            close_time=await get_truncated_time(shop.close_time)))

            await conn.commit()
            return {"shop_id": new_shop_id.first()[0]}
        except Exception:
            raise HTTPException(status_code=400, detail="Something went wrong :(")


@router.put("/edit_shop")
async def edit_shop(
        shop: UpdateShopSchema,
        db_session=Depends(get_async_session),):

    async with db_session as conn:

        existing_shop = await conn.execute(select(ShopOrm.name,
                                                  ShopOrm.city_id,
                                                  ShopOrm.street_id,
                                                  ShopOrm.building,
                                                  ShopOrm.open_time,
                                                  ShopOrm.close_time
                                                  ).select_from(ShopOrm).where(ShopOrm.id == shop.id))
        existing_shop = existing_shop.first()

        if existing_shop is None:
            raise HTTPException(status_code=400, detail="Shop not found")

        shop_update_data_dict = dict(shop.dict(exclude_unset=True))

        await conn.execute(update(ShopOrm).values(name=shop_update_data_dict.get("name", existing_shop[0]),
                                                  city_id=shop_update_data_dict.get("city_id", existing_shop[1]),
                                                  street_id=shop_update_data_dict.get("street_id", existing_shop[2]),
                                                  building=shop_update_data_dict.get("building", existing_shop[3]),
                                                  open_time=await get_truncated_time(shop_update_data_dict.get("open_time", existing_shop[4])),
                                                  close_time=await get_truncated_time(shop_update_data_dict.get("close_time", existing_shop[5]))).where(ShopOrm.id == shop.id))

        await conn.commit()
        return {"message": "The store has been successfully edited"}


@router.get("", response_model=GetShopListSchema)
async def get_shop(street: List[str] = Query(None),
                   city: List[str] = Query(None),
                   open: CloseOrOpen = Query(None),
                   db_session=Depends(get_async_session)):

    # Если не передали параметров - вернем все магазины
    if street is None and city is None and open is None:
        try:
            async with db_session as conn:
                shops = await conn.execute(select(ShopOrm.name,
                                                  CityOrm.name,
                                                  StreetOrm.name,
                                                  ShopOrm.building,
                                                  ShopOrm.open_time,
                                                  ShopOrm.close_time
                                                  ).select_from(ShopOrm))\
                                                .join(CityOrm, CityOrm.id == ShopOrm.city_id)\
                                                .join(StreetOrm, and_(CityOrm.id == StreetOrm.city_id, ShopOrm.city_id==StreetOrm.city_id))

                json_field = ("name", "city_name", "street_name", "building", "open_time", "close_time")
                shops = {"shops": [dict(zip(json_field, shop)) for shop in shops.all()]}
                return shops

        except Exception:
            raise HTTPException(status_code=400, detail="Shop not found")

    try:
        async with db_session as conn:
            street_subquery = street if street is not None else select(StreetOrm.name).select_from(StreetOrm).subquery()
            city_subquery = city if city is not None else select(CityOrm.name).select_from(CityOrm).subquery()

            if open == 1:
                open_subquery = select(ShopOrm.id).select_from(ShopOrm).where(func.current_time().between(ShopOrm.open_time, ShopOrm.close_time)).subquery()
            elif open == 0:
                open_subquery = select(ShopOrm.id).select_from(ShopOrm).where(not_(func.current_time().between(ShopOrm.open_time, ShopOrm.close_time))).subquery()
            elif open is None:
                open_subquery = select(ShopOrm.id).select_from(ShopOrm).subquery()

            shops = await conn.execute(select(ShopOrm.name,
                                              CityOrm.name,
                                              StreetOrm.name,
                                              ShopOrm.building,
                                              ShopOrm.open_time,
                                              ShopOrm.close_time
                                              ).select_from(ShopOrm)
                                                .join(CityOrm, and_(CityOrm.id == ShopOrm.city_id, CityOrm.name.in_(city_subquery)))
                                                .join(StreetOrm, and_(CityOrm.id == StreetOrm.city_id, ShopOrm.city_id==StreetOrm.city_id, StreetOrm.name.in_(street_subquery)))
                                                .where(ShopOrm.id.in_(open_subquery)))
            json_field = ("name", "city_name", "street_name", "building", "open_time", "close_time")
            shops = {"shops": [dict(zip(json_field, shop)) for shop in shops.all()]}
            return shops
    except Exception:
        raise HTTPException(status_code=400, detail="Shop not found")
