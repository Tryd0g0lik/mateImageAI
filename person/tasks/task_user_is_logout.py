import asyncio
import logging
from datetime import datetime
from json import JSONDecodeError
from redis.asyncio.client import Redis
from redis.backoff import ExponentialBackoff
from redis.retry import Retry
from celery import shared_task

from logs import configure_logging

from person.redis_person import RedisOfPerson
from person.tasks.task_user_is_authenticate import async_task_user_authenticate

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


@shared_task(
    name=__name__,
    bind=True,
    ignore_result=True,
    autoretry_for=(
        Exception,
        TimeoutError,
    ),
    retry_backoff=False,
)
def task_user_logout(self, user_id: int) -> dict | bool:
    log.info("START CACHE: %s" % task_user_logout.__name__)
    """ "
        Here, we get a dict from non-relational(Redis 1) DB and updating the properties (then saved to the Redis 1).
        If all 'OK' we return True or empty dict (when wea have an Error), to the outside.
        """
    try:
        asyncio.get_event_loop().run_until_complete(async_task_user_logout(user_id))
    except (ConnectionError, Exception) as error:
        log.error(
            ValueError(
                "%s: ERROR => %s"
                % (task_user_logout.__name__, error.args.__getitem__(0))
            )
        )
        return {}
    return True


async def async_task_user_logout(user_id: int) -> dict | bool:
    client: type(Redis.client) = None
    log.info(
        "START CACHE: %s. KEY: %s"
        % (async_task_user_logout.__name__, f"user:{user_id}:person")
    )
    key = f"user:{user_id}:person"

    try:
        # Redis client with retries on custom errors
        client = RedisOfPerson()
    except (ConnectionError, Exception) as error:
        log.error(
            ValueError(
                "%s: ERROR => %s" % (async_task_user_logout.__name__, error.args)
            )
        )
        return {}

    try:
        # Check a key into the db for the cached user
        user_json = await client.async_basis_collection(user_id)
        if len(user_json.keys()) == 0:
            raise
    except (ValueError, Exception) as error:
        log.error(
            ValueError("%s: ERROR => %s" % (async_task_user_logout.__name__, error))
        )
        return {}

    try:
        # LOGOUT
        log.info("%s: BEFORE DATA UPDATE" % (async_task_user_logout.__name__))
        # if user_json.get("is_active"):
        user_json.__setitem__("is_active", False)
        log.info(
            "%s: CHANGE 'is_active'. Now is: %s"
            % (async_task_user_logout.__name__, user_json["is_active"])
        )

        # SAVING
        log.info(
            "%s: BEFORE DATA SAVING: %s" % (async_task_user_logout.__name__, user_json)
        )
        await client.async_set_cache_user(key, **user_json)
        log.info(
            "%s: AFTER DATA SAVING: %s" % (async_task_user_logout.__name__, user_json)
        )
        return True
    except (JSONDecodeError, Exception) as error:
        log.error(
            ValueError("%s: ERROR => %s" % (async_task_user_logout.__name__, error))
        )
        return {}
    finally:
        await client.aclose()
        log.info(
            "COMPLETED CACHE: %s. KEY: %s"
            % (async_task_user_logout.__name__, f"user:{user_id}:person")
        )
