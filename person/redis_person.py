import json
import logging
import ssl
from typing import Dict, Union, Optional, Mapping
from redis.asyncio.client import Redis
from redis.credentials import CredentialProvider
from redis.asyncio.retry import Retry
from redis.exceptions import ConnectionError
from redis.utils import get_lib_version

from dotenv_ import DB_TO_RADIS_HOST
from logs import configure_logging
from redis.asyncio.connection import (
    ConnectionPool,
)

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class RedisOfPerson(Redis):
    def __init__(
        self,
        host: str = f"{DB_TO_RADIS_HOST}",
        port: int = 6380,
        db: Union[str, int] = 1,
    ):
        super().__init__(host=host, port=port, db=db)
        self.client_state = None

    async def ping(self, **kwargs) -> ConnectionError | bool:
        ping = await super().ping(**kwargs)
        if not ping:
            raise ConnectionError("Redis connection failed")
        return True

    async def async_has_key(self, one_key: str = "") -> bool:
        """
        :param one_key: Key for get data from redis's db. Example. User after registration hase the 'user:<user_index>:person' of key.
        If you can't get data? check the db number. It where you are connected. Example.
        :return: bool. If we have - True, it means - we have a key in the general list
        """

        log.info(
            "%s: BEFORE GET KEYS: KEY %s" % (RedisOfPerson.__class__.__name__, one_key)
        )
        k_list_encode = await self.keys()
        log.info(
            "%s: GOT b_KEYS: KEY LIST %s"
            % (RedisOfPerson.__class__.__name__, k_list_encode.__str__())
        )
        k_list = [s.decode() for s in k_list_encode]
        log.info(
            "%s: GOT KEYS: %s"
            % (RedisOfPerson.__class__.__name__, True if one_key in k_list else False)
        )
        return True if one_key in k_list else False

    async def async_get_cache_user(self, key: str) -> dict | bool:
        """
        :param str key: Key for get data from redis's db. Example. User after registration hase the 'user:<user_index>:person' of key.
        If you can't get data? check the db number. It where you are connected. Example.
        For person's cache is number '1'.
        :return: dict/json | False.
        """
        result = await self.async_has_key(key)
        get_ = await self.get(key)
        return json.loads(get_) if result else False

    async def async_set_cache_user(
        self, key: str, **kwargs: Dict[str, Union[str, int]]
    ) -> bool:
        """
        Redis's cache
        Now will be saving on the 27 hours.
        'task_user_from_cache' task wil be to upgrade postgres at ~ am 01:00
        Timetable look the 'project.celery.app.base.Celery.conf'
        :param str key: This is key element, by key look up where it will be saved
        :return None
        """
        try:
            await self.set(key, json.dumps(kwargs), 97200)
            return True
        except Exception as error:
            raise ValueError("%s: ERROR => %s" % (__name__, error.args[0]))


# async def async_get_users(self, **kwargs: Dict[str: str | int]) -> List[Users] | None:
#     """
#     Get user from Users's db.
#     Entry point, for getting only one user from Redis's cache. You can \
#     insert (in the entrypoint) only two various of dictionary.
#     ```json
#     {
#         'username': 'your_username',
#     }
#     ```
#     or
#     ```json
#     {
#         'id': 24,
#     }
#     ```
#     Above example is - dictionaries if you want to get one Users's image.
#     Note: If you want insert 2 in 1 (dictionaries) for a work will be used element whose index is zero!
#
#
#     :param Dict[str: str | int] kwargs: 'username' or 'id' index of use. It's unique data in basis db.
#     :return list[Users] | None: Return the list of users
#     """
#     if not 'username' and not 'id' in kwargs:
#         return None
#     return await RedisOfPerson.__async_get_person(**kwargs)
#
#
# @staticmethod
# async def __async_get_person(**kwargs: Dict[str: str | int]) -> list[Users] | None:
#     """
#     Get user from Users's db.
#     Entry point, for getting only one user from Redis's cache. You can \
#     insert (in the entrypoint) only two various of dictionary.
#     ```json
#     {
#         'username': 'your_username',
#     }
#     ```
#     or
#     ```json
#     {
#         'id': 24,
#     }
#     ```
#     Above example is - dictionaries if you want to get one Users's image.
#     Note: If you want insert 2 in 1 (dictionaries) for a work will be used element whose index is zero!
#
#
#     :param Dict[str: str | int] kwargs: 'username' or 'id' index of use. It's unique data in basis db.
#     :return list[Users] | None: Return the list of users
#     """
#     try:
#         if not kwargs:
#             return []
#         if len(kwargs.keys()) > 0:
#             k = list(kwargs.keys())[0]
#             v = list(kwargs.values())[0]
#             person_list = [item async for item in Users.objects.filter(**{k: v})][0]
#             return person_list
#     except Exception as error:
#         raise ValueError("%s: ERROR => %s." % (RedisOfPerson.get_one_person.__name__, error.args[0]))
