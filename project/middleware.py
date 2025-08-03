# middleware.py
import json
import logging
import asyncio
from django.contrib.auth.models import AbstractUser
from django.contrib.sessions.backends.cached_db import SessionStore
from django.core.cache import caches
from django.db.models.expressions import result
from django.http import HttpRequest

from person.binaries import Binary
from person.redis_person import RedisOfPerson
from logs import configure_logging

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class RedisAuthMiddleware:
    # https://docs.djangoproject.com/en/4.2/topics/http/middleware/#:~:text=Middleware
    def __init__(self, get_response):
        self.get_response = get_response
        self.client = None
        self.user_key = ""

    def __call__(self, request: HttpRequest) -> HttpRequest:
        """
        Here is we checking the user's session key in cookies.By this key we will get the cache of user's object.
        The cache of user's object it is JSON str 'session: {"user": < binary code Users's object >}' < === > 'cockie_key: {key: binary data}'.
        :param HttpRequest request:
        :return:
        """
        pass
        self.client = RedisOfPerson(db=0)
        try:
            if request.COOKIES and request.COOKIES.get("session_user"):
                # GET USER's SESSION KEY FRON COOKIE
                str_session_key = request.COOKIES.get("session_user")
                b = Binary()

                b_session_key = b.binary_to_str(str_session_key.encode())
                # session_key = b_session_key.decode("utf-8")
                # get cache of user's session key from the redis 0
                loop = asyncio.get_event_loop()
                async_has_key = loop.run_until_complete(
                    self.client.async_has_key(b_session_key)
                )

                if not async_has_key:
                    return self.get_response(request)
                # get cache of user
                loop = asyncio.get_event_loop()
                session_user = loop.run_until_complete(
                    self.client.async_get_cache_user(b_session_key)
                )
                loop.close()
                session_user_json = json.loads(session_user)
                b = Binary()
                user_obj = b.binary_to_object(session_user_json.__getattr__("b_user"))
                request.__setattr__("user", user_obj)
                request.user.is_authenticated = True
                request.user.is_active = True
                # return self.get_response(request)
        except Exception as error:
            log.error(
                "%s: %s"
                % (
                    RedisAuthMiddleware.__class__.__name__ + self.__call__.__name__,
                    list(error.args).__getitem__(0),
                )
            )
            return self.get_response(request)
        finally:
            self.client.close()

        # if request.user.is_authenticated:
        #     client_to_get = self.client.get
        #
        #     data_session = asyncio.create_task(client_to_get, user_key.split(":").__getitem__(1))
        #     request.user = json.load(data_session["b_user"]).decode()
        #     # Проверяем актуальность данных в Redis
        # user_key = f"user:{request.user.pk}:person"
        #
        # if not self.cache.get(user_key):
        #     # Обновляем кэш если данные устарели
        #     user_data = {
        #         'id': request.user.pk,
        #         'username': request.user.username,
        #         # ... другие поля
        #     }
        #     self.cache.set(user_key, user_data)

        # if (not request.user or not request.user.is_authenticated) \
        #     and (request.COOKIES.get(r"user:[0-9]+:session")):
        #     session_cookie = request.COOKIES.get(r"user:[0-9]+:session")
        #     k = list(dict(session_cookie).keys()).__getitem__(0)
        #     resp_bool = await self.client.async_has_key(k)
        #     if not resp_bool:
        #         return self.get_response(request)
        #     request.user.is_authenticated = True
        #     data_session = await self.client.get(k.split(":").__getitem__(1))
        #     user_fron_session = json.load(data_session["b_user"]).decode()
        #     request.user = user_fron_session

        return self.get_response(request)
