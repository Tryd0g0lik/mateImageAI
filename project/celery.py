import json
import os

from celery import Celery, shared_task

from project import celeryconfig
import redis
from redis.retry import Retry
from redis.backoff import ExponentialBackoff

from stalk.tasks_generations.first_task import logger

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

app = Celery(
    "proj",
    include=[
        "stalk.tasks_generations.first_task",
        "stalk.tasks_generations.task_next",
    ],
)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
# app.config_from_object('django.conf:settings', namespace='CELERY',)
app.config_from_object(celeryconfig)
# Load task modules from all registered Django apps.
# app.autodiscover_tasks()


@shared_task(name=__name__, bind=True, ignore_result=False)
def debug_task(self, person_data):
    try:
        # Устойчивое подключение
        redis_client = redis.Redis(
            host="83.166.245.209", port=6380, socket_timeout=10, retry_on_timeout=True
        )

        if not redis_client.ping():
            raise ConnectionError("Redis connection failed")

        # Атомарная запись
        with redis_client.pipeline() as pipe:
            pipe.set(
                f"user:{person_data['id']}:person", json.dumps(person_data), ex=86400
            )
            pipe.execute()

    except Exception as e:
        logger.error(f"Redis operation failed: {str(e)}")
        raise self.retry(exc=e)
    print(f"Request: {self.request!r}")
