import asyncio
from celery import Celery

from celery.schedules import crontab

from src.config import redis_host, redis_port
from src.parser.on_map_russia.service import start_scraping

celery = Celery("tasks", broker=f"redis://{redis_host}:{redis_port}")


@celery.task(name="monitoring_on_map_russia")
def monitoring_on_map_russia():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_scraping())


@celery.task(name="start_on_map_russia")
def start_on_map_russia():
    monitoring_on_map_russia.apply_async()


celery.conf.beat_schedule = {
    'start_on_map_russia': {
        'task': 'start_on_map_russia',
        'schedule': crontab(hour="2"),
    },
}
