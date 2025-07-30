import json
import logging
import os

from datetime import datetime
from typing import TypedDict
from celery import shared_task
from celery.utils.log import get_task_logger
from django.dispatch import Signal
from django.template.defaultfilters import length
from kombu.utils.json import dumps
from redis import Redis, TimeoutError

from dotenv_ import DB_TO_RADIS_CACHE_USERS, DB_TO_RADIS_PORT, DB_TO_RADIS_HOST
from logs import configure_logging
from person.interfaces import TypeUser
from person.models import Users
from person.serializers import CacheUsersSerializer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

log = logging.getLogger(__name__)
configure_logging(logging.INFO)

logger = get_task_logger(__name__)


@shared_task(
    name=__name__,
    bind=False,
    ignore_result=True,
    autoretry_for=(TimeoutError,),
    retry_backoff=False,
)
def task_postman_for_user_id(self, user_id_list: list[int]) -> TypeUser:
    """
    retry_backoff - https://docs.celeryq.dev/en/stable/userguide/tasks.html#Task.autoretry_for
    ignore_result - If False, it means we don't have a response. Or conversely if we have a True.
    https://docs.celeryq.dev/en/stable/userguide/tasks.html#Task.ignore_result

    This Task is a POSTMAN. Here only transmits the user id. It happens from the entry point to the handler function
    :param self:
    :param user_id_list: Index from new user, we receive in list format.
    :return:
    """
    if len(user_id_list) == 0:
        raise ValueError("[%s]: No users found" % __name__)
    return person_to_redis(user_id_list)


def person_to_redis(user_id_list: list[int]) -> TypeUser:
    """
    Here, we will be caching of new user after registration/ From entrypoint,we get an id.
    After that, we find the user by id and send it to the cache.
    :param self:
    :param user_id_list: Index from new user, we receive in list format.
    :return:
    """
    log.info("START CACHE: %s" % __name__)
    client = Redis(
        host=f"{DB_TO_RADIS_HOST}",
        port=f"{DB_TO_RADIS_PORT}",
        db=DB_TO_RADIS_CACHE_USERS,
    )

    try:
        if not client.ping():
            raise ConnectionError("Redis connection failed")
        log.info("Client is ping")
        # Basis db
        person_list = Users.objects.filter(id=user_id_list[0])
        if not person_list.exists():
            raise ValueError(
                "[%s]: No users found in Users's db. Length from 'person_list' is %s "
                % (__name__, str(len(person_list)))
            )
        user_serializer = CacheUsersSerializer(person_list[0])
        user_dict: TypeUser = user_serializer.data.copy()
        log.info("Received user ID: %s" % user_dict["id"])
        # Redis's cache
        # Now will be saving on the 27 hours.
        # 'task_user_from_cache' task wil be to upgrade postgres at ~ am 01:00
        # Timetable look the 'project.celery.app.base.Celery.conf'
        client.set(f"user:{str(user_dict["id"])}:person", json.dumps(user_dict), 97200)
        client.close()
        log.info("User with %s ID was saved in Redis. The End" % str(user_dict["id"]))
        return user_dict
    except Exception as error:
        log.error("[%s]: ERROR => %s" % (__name__, error.args[0]))
        raise ValueError("[%s]: ERROR => %s" % (__name__, error.args[0]))
