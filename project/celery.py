import json
import os

from celery import Celery
from celery.schedules import crontab

from project import celeryconfig


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
app.conf.beat_schedule = {
    "midnigth-tast": {
        "task": "person.tasks.task_user_from_cache_to_td_repeat.task_user_from_cache",
        "schedule": crontab(hour=1, minute=0),
    }
}
