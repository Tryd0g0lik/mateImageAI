import asyncio
import json
import logging
from datetime import datetime
from json import JSONDecodeError
from typing import List, Tuple

from redis.asyncio.client import Redis
from redis.exceptions import ConnectionError, BusyLoadingError
from redis.backoff import ExponentialBackoff
from redis.retry import Retry
from celery import shared_task
from logs import configure_logging
from person.redis_person import RedisOfPerson


from dotenv_ import DB_TO_RADIS_CACHE_USERS, DB_TO_RADIS_PORT, DB_TO_RADIS_HOST

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


@shared_task(
    name=__name__,
    bind=True,
    ignore_result=False,
    autoretry_for=(TimeoutError,),
    retry_backoff=False,
)
def task_user_authenticate(self, user_id: int) -> dict | bool:
    log.info("START CACHE: %s" % __name__)

    """ "
    Get object from db or 404 status-code.
    We are checking user.
    Below, we will be change the active status of user.
    """
    asyncio.get_event_loop().run_until_complete(async_task_user_authenticate(user_id))
    return True


async def async_task_user_authenticate(user_id: int) -> dict | bool:
    client: type(Redis.client) = None
    key = f"user:{user_id}:person"
    res_bool: bool = False
    try:
        # Redis client with retries on custom errors
        retry = Retry(ExponentialBackoff(), 3)
        client = RedisOfPerson(retry)
        log.info("START REDIS: %s" % __name__)
    except (ConnectionError, Exception) as error:
        raise ValueError("%s: ERROR => %s" % (__name__, error.args[0]))
    # Check tha ping for cache's db
    if not await client.ping():
        raise ConnectionError("Redis connection failed")
    log.info("REDIS IS PING: %s" % __name__)
    try:
        # Check a key into the db for the cached user
        res_bool = await client.async_has_key(key)
        log.info("CLIENT HASE a KEY: %s" % __name__)
        # User was not found in cache/ It means the registration was unsuccessful.
        # On the stage be avery one user is saved in cache
        if not res_bool:
            raise ValueError("%s: ERROR => User not was founded" % (__name__))
    except Exception as error:
        log.error(ValueError("%s: ERROR => %s" % (__name__, error)))
        return {}

    try:
        log.info("BEFORE GET USER FROM CACHE")
        user_json = await client.async_get_cache_user(key)
        log.info("GOT USER FROM CACHE: %s" % user_json)
        if not user_json:
            log.info(
                ValueError("%s: ERROR => User not was founded in cache" % (__name__))
            )
            return {}

        user_json = dict(user_json)
        if not isinstance(user_json, dict):
            log.error(
                ValueError(f"%s: Expected dict, got {type(user_json)}" % (__name__))
            )
            return {}
        # get the text from the basis value
        if user_json.get("is_active", False):
            user_json.__setitem__("is_active", True)
        if user_json.get("is_activated", False):
            user_json.__setitem__("is_activated", True)
        if user_json.get("is_verified", False):
            user_json.__setitem__("is_verified", True)
        user_json.__setitem__(
            "date_joined", datetime.now().strftime("%Y-%m-%d %H:%M:%S.%u")
        )
        user_json.__setitem__(
            "last_login", datetime.now().strftime("%Y-%m-%d %H:%M:%S.%u")
        )

        await client.async_set_cache_user(key, **user_json)
        return True
    except (JSONDecodeError, Exception) as error:
        log.error(ValueError("%s: ERROR => %s" % (__name__, error)))
        return {}
    finally:
        await client.close()
