# Celery application configuration
import os
from celery import Celery

# Redis URL configuration
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Create Celery app
celery_app = Celery(
    "casino_club",
    broker=redis_url,
    backend=redis_url,
    include=["app.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "sample-task": {
            "task": "app.tasks.sample_task",
            "schedule": 30.0,  # Run every 30 seconds
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks()
