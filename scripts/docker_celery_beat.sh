#!/bin/bash

celery -A src.broker.tasks:celery beat --loglevel=INFO

