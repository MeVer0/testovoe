import asyncio

from celery import Celery
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_
from src.auth.auth_backend import fastapi_users
from src.auth.models import User

from src.database import get_async_session
from src.parser.on_map_russia.service import start_scraping
from src.config import redis_host, redis_port

celery = Celery("tasks", broker=f"redis://{redis_host}:{redis_port}")

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    # dependencies=[Depends(fastapi_users.current_user(active=True, verified=True, superuser=True))]
    dependencies=[Depends(fastapi_users.current_user(active=True, verified=True))]
)


@celery.task(name="update_on_map_russia")
def task_start_scraping():
    asyncio.run(start_scraping())


@router.post("/update_on_map_russia")
def update_on_map_russia():
    try:
        task_start_scraping().delay()
        return {"message": "successfully launched the update : )"}
    except Exception as r:
        raise HTTPException(status_code=400, detail="Something went wrong :(")
