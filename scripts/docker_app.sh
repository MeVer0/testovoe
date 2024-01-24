#!/bin/bash

# Запускаем миграции и приложение
alembic upgrade head

gunicorn src.api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000