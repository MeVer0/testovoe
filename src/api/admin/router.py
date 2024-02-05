import asyncio
import traceback

# Неиспользуемые + смешанные импорты
from celery import Celery
from fastapi import APIRouter, Depends, HTTPException

from src.config import redis_host, redis_port
from src.auth.auth_backend import fastapi_users
from src.parser.on_map_russia.service import start_scraping


celery = Celery("tasks", broker=f"redis://{redis_host}:{redis_port}")

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    # dependencies=[Depends(fastapi_users.current_user(active=True, verified=True, superuser=True))]
    # Желаельно не вылазить за 80 символов,
    # иногда можно больше, но не больше 120!
    dependencies=[
        Depends(fastapi_users.current_user(active=True, verified=True))
    ]
)


@celery.task(name="update_on_map_russia")
def task_start_scraping():
    asyncio.run(start_scraping())


@router.post("/update_on_map_russia")
def update_on_map_russia():
    try:
        task_start_scraping().delay()
        return {"message": "successfully launched the update : )"}
    except Exception:
        # Если хендлишь эксепшн и записываешь в переменную,
        # то надо это переменную использовать
        # Либо не создавать переменную и использовать traceback
        raise HTTPException(
            status_code=400,
            detail=f"Something went wrong :( -> {traceback.format_exc()}"
        )
