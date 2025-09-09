# Celery worker configuration
import os
from celery import Celery

# Celery configuration
celery_app = Celery(
    "casino_club",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    include=["app.tasks"]  # Include task modules
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "app.tasks.*": {"queue": "default"},
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks()

if __name__ == "__main__":
    celery_app.start()
