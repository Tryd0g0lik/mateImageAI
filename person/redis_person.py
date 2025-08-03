import json
import logging
from typing import Dict, Union, Any
from redis.asyncio.client import Redis
from redis.exceptions import ConnectionError

from dotenv_ import DB_TO_RADIS_HOST
from logs import configure_logging

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

    async def ping(self, **kwargs) -> bool:
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
            "%s: BEFORE GET KEYS: KEY %s"
            % (RedisOfPerson.__class__.__name__ + self.async_has_key.__name__, one_key)
        )
        k_list_encode = await self.keys()
        if len(k_list_encode) == 0:
            log.info(
                "%s: KEYS was not found: %s"
                % (
                    RedisOfPerson.__class__.__name__ + self.async_has_key.__name__,
                    one_key,
                )
            )
            return False
        log.info(
            "%s: GOT b_KEYS: length KEY's LIST %s"
            % (
                RedisOfPerson.__class__.__name__ + self.async_has_key.__name__,
                len(k_list_encode),
            )
        )
        k_list = [s.decode() for s in k_list_encode]
        log.info(
            "%s: GOT KEYS: %s"
            % (
                RedisOfPerson.__class__.__name__ + self.async_has_key.__name__,
                True if one_key in k_list else False,
            )
        )
        return True if one_key in k_list else False

    async def async_get_cache_user(self, key: str) -> dict[str, Any] | bool:
        """
        :param str key: Key for get data from redis's db. Example. User after registration hase the 'user:<user_index>:person' of key.
        If you can't get data? check the db number. It where you are connected. Example.
        For person's cache is number '1'.
        :return: dict/json | False.
        """
        # result = await self.async_has_key(key)
        get_ = await self.get(key)
        return json.loads(get_.decode())

    async def async_set_cache_user(
        self, key: str, **kwargs: Dict[str, Union[str, int]]
    ) -> bool:
        """
        Redis's cache
        Session of user saving in cache's session db (Redis 0). "kwargs={'user': <Users's object >}

        Caching of user's db in cache's db (Redis 1). Below, it's cache's db.
        Now will be saving on the 27 hours.
        'task_user_from_cache' task wil be to upgrade postgres at ~ am 01:00
        Timetable look the 'project.celery.app.base.Celery.conf'
        :param str key: This is key element, by key look up where it will be saved
        :return None
        """
        try:
            user = kwargs.__getitem__("user")
            if user:
                """
                User's object save in cache's session (Redis 0)
                """
                b_user = user.encode()
                await self.set(key, json.dumps({"b_user": b_user}))
                return True
        except Exception as error:
            log.info(
                ValueError(
                    "%s: ERROR => %s"
                    % (
                        RedisOfPerson.__class__.__name__
                        + self.async_set_cache_user.__name__,
                        error.args[0],
                    )
                )
            )
            return False
        try:
            """
            Cache's db
            """
            await self.set(key, json.dumps(kwargs), 97200)
            return True
        except Exception as error:
            log.info(
                ValueError(
                    "%s: ERROR => %s"
                    % (
                        RedisOfPerson.__class__.__name__
                        + self.async_set_cache_user.__name__,
                        error.args[0],
                    )
                )
            )
            return False

    async def async_basis_collection(self, user_id: int) -> dict[str, Any]:
        """
        Here, woas collected the code which ofter we could meet in ti the operation by the data update to Redis. It's by 'person'.
        :param int user_id: user's index,
        :return: dict/json string. This is an image of user.
        """
        key = f"user:{user_id}:person"

        # Check tha ping for cache's db
        if not await self.ping():
            raise ConnectionError("Redis connection failed")
        try:
            # Check a key into the db for the cached user
            res_bool = await self.async_has_key(key)

            # User was not found in cache/ It means the registration was unsuccessful.
            # On the stage be avery one user is saved in cache
            if not res_bool:
                raise (
                    ValueError(
                        "%s: ERROR => User not was founded"
                        % (
                            RedisOfPerson.__class__.__name__
                            + self.async_basis_collection.__name__,
                        )
                    )
                )

        except Exception as error:
            log.error(error)
            return {}
        log.info(
            "%s: GOT MESSAGE: %s"
            % (
                RedisOfPerson.__class__.__name__ + self.async_basis_collection.__name__,
                "Passed the check ",
            )
        )
        try:
            user_json = await self.async_get_cache_user(key)
            if not user_json:
                log.info(
                    ValueError(
                        "%s: ERROR => User not was founded in cache: %s"
                        % (
                            RedisOfPerson.__class__.__name__
                            + self.async_basis_collection.__name__,
                            user_json,
                        )
                    )
                )
                return {}
            log.info(
                "%s: GOT 'user_json'. It's BOOL: %s"
                % (
                    RedisOfPerson.__class__.__name__
                    + self.async_basis_collection.__name__,
                    isinstance(user_json, dict),
                )
            )
            if not isinstance(user_json, dict):
                log.error(
                    ValueError(
                        f"%s: Expected dict, got {type(user_json)}"
                        % (
                            RedisOfPerson.__class__.__name__
                            + self.async_basis_collection.__name__
                        )
                    )
                )
            else:
                log.info(
                    "%s: GOT 'user_json' #%s"
                    % (
                        RedisOfPerson.__class__.__name__
                        + self.async_basis_collection.__name__,
                        user_id,
                    )
                )
                return user_json
            return {}
        except Exception as error:
            log.error(
                ValueError(
                    "%s: ERROR => %s"
                    % (
                        RedisOfPerson.__class__.__name__
                        + self.async_basis_collection.__name__,
                        error,
                    )
                )
            )
            return {}


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
