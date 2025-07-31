import json
import time
import asyncio
import re
from datetime import datetime, timedelta
from collections.abc import Callable
from typing import Any, TypedDict, NotRequired, List, Dict

from django.contrib.auth.models import AnonymousUser
from django.db import connections
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpRequest, HttpResponse
from drf_yasg import openapi

from dotenv_ import SECRET_KEY_DJ, POSTGRES_DB
from person.access_tokens import AccessToken
from person.hasher import Hasher
from person.interfaces import U, UserData, TypeUser
from person.models import Users
from person.apps import signal_user_registered
from rest_framework import serializers, status
from rest_framework.response import Response
from adrf.viewsets import ViewSet

from person.redis_person import RedisOfPerson
from person.serializers import (
    UsersSerializer,
    UsersForSuperuserSerializer,
    Async_UsersSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from person.serializers import (
    UserResponseSerializer200,
    ErrorResponseSerializer,
)
from person.tasks.task_cache_hew_user import task_postman_for_user_id
from person.tasks.task_user_is_login import task_user_login

from project.settings import SIMPLE_JWT
from person.binaries import Binary
import logging
from logs import configure_logging
from dotenv import load_dotenv


load_dotenv()
log = logging.getLogger(__name__)
configure_logging(logging.INFO)


async def sync_for_async(fn: Callable[[Any], Any], *args, **kwargs):
    return await asyncio.create_task(asyncio.to_thread(fn, *args, **kwargs))


def new_connection(data) -> list:
    """
    new user cheks on the duplicate
    :param data:
    :return:
    """
    with connections["default"].cursor() as cursor:
        cursor.execute(
            """SELECT * FROM person_users WHERE username = '%s' AND email = '%s';"""
            % (data.get("username"), data.get("email"))
        )
        # POSTGRES_DB
        resp_list = cursor.fetchall()
        users_list = [view for view in resp_list]
    return users_list


async def iterator_get_person_cache(client: type(RedisOfPerson)):
    """
    Get all collections of keys from person's cache.
    :return:
    """
    keys = await client.keys("user:*")
    for key in keys:
        yield key


class UserViews(ViewSet):

    @swagger_auto_schema(
        operation_description="""
        User admin can get all users list.
        Permissions if you is superuser.
        """,
        tags=["person"],
        responses={
            200: openapi.Response(
                description="Users array",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    # required=['id', "username", "password", "first_name", "last_login"],
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=12),
                            "username": openapi.Schema(
                                example="nH2qGiehvEXjNiYqp3bOVtAYv....",
                                type=openapi.TYPE_STRING,
                            ),
                            "first_name": openapi.Schema(
                                type=openapi.TYPE_STRING, example=""
                            ),
                            "last_name": openapi.Schema(
                                type=openapi.TYPE_STRING, example=""
                            ),
                            "last_login": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                example="2025-07-20 00:39:14.739 +0700",
                            ),
                            "is_superuser": openapi.Schema(
                                type=openapi.TYPE_BOOLEAN,
                                example=False,
                            ),
                            "is_staff": openapi.Schema(
                                type=openapi.TYPE_BOOLEAN,
                                example=False,
                                description="user got permissions how superuser or not.",
                            ),
                            "is_active": openapi.Schema(
                                type=openapi.TYPE_BOOLEAN,
                                example=False,
                            ),
                            "date_joined": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                example="2025-07-20 00:39:14.739 +0700",
                            ),
                            "created_at": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                example="2025-07-20 00:39:14.739 +0700",
                            ),
                            "balance": openapi.Schema(
                                type=openapi.TYPE_NUMBER, example="12587.268"
                            ),
                            "verification_code": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                example="_null_jOePj2i769OQ4XsFPihlA....",
                                description="""
                            '<username>_null_jOePj2i769OQ4XsFPihlA....'
                            This is a code from  referral link.
                            """,
                            ),
                            "is_sent": openapi.Schema(
                                type=openapi.TYPE_BOOLEAN,
                                example=True,
                                description="""
                            Referral link was sent by user email address.
                            """,
                            ),
                        },
                    ),
                ),
            ),
            401: "User admin is invalid",
            500: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                title="Mistake",
                properties={
                    "data": openapi.Schema(
                        type=openapi.TYPE_STRING,
                    )
                },
            ),
        },
    )
    async def list(self, request: HttpRequest) -> HttpResponse:
        """
        Superuser can get the users array of data.
        :param request:
        :return:
        ```js
            [
                {
                    "id": 46,
                    "last_login": "2025-07-20T11:23:13.016496+07:00",
                    "is_superuser": false,
                    "username": "Sergey",
                    "first_name": "",
                    "last_name": "",
                    "email": "work80@mail.ru",
                    "is_staff": true,
                    "is_active": true,
                    "date_joined": "2025-07-19T12:56:26.340392+07:00",
                    "is_sent": true,
                    "is_verified": true,
                    "verification_code": "_null_jOePj2i769OQ4XsFPihlAVpH6RGN_idjsycxU6-WfRo",
                    "balance": 0,
                    "created_at": "2025-07-19T11:34:32.928150+07:00",
                    "updated_at": "2025-07-20T11:23:13.016496+07:00"
                },
                {
                    "id": 47,
                    "last_login": "2025-07-20T11:09:29.910079+07:00",
                    "is_superuser": false,
                    "username": "Denis",
                    "first_name": "",
                    "last_name": "",
                    "email": "work80@mail.ru",
                    "is_staff": false,
                    "is_active": true,
                    "date_joined": "2025-07-20T11:09:29.460076+07:00",
                    "is_sent": true,
                    "is_verified": true,
                    "verification_code": "_null_jOePj2i769OQ4XsFPihlAVpH6RGN_idjsycxU6-WfRo",
                    "balance": 0,
                    "created_at": "2025-07-20T10:57:47.979716+07:00",
                    "updated_at": "2025-07-20T11:09:30.390933+07:00"
                }
            ]
        ```
        """
        user: U | AnonymousUser = request.user
        if user.is_active and user.is_staff:
            try:
                queryset_list = [views async for views in Users.objects.all()]
                serializer = UsersForSuperuserSerializer(queryset_list, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as error:
                return Response(
                    {"data": error.args}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(
            {"data": "User admin is invalid"}, status=status.HTTP_401_UNAUTHORIZED
        )

    @swagger_auto_schema(
        operation_description=""""
            You can gat data if you is the superuser or
             index (it's parameter from the url path) for what retrieve data single user (if user index is pk).

        """,
        tags=["person"],
        manual_parameters=[
            openapi.Parameter(
                name="id",
                title="pk",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                example=54,
                format=openapi.FORMAT_INT64,
            )
        ],
        responses={
            200: UsersForSuperuserSerializer,
            401: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
    )
    async def retrieve(self, request: HttpRequest, pk: str) -> HttpResponse:
        """
        :param request:
        :param int pk: User index (it's parameter from the url path) for what retrieve data single user (index which is pk)
        :return:
        ```js
            [
                {
                    "id": 46,
                    "last_login": "2025-07-20T11:23:13.016496+07:00",
                    "is_superuser": false,
                    "username": "Sergey",
                    "first_name": "",
                    "last_name": "",
                    "email": "work80@mail.ru",
                    "is_staff": true,
                    "is_active": true,
                    "date_joined": "2025-07-19T12:56:26.340392+07:00",
                    "is_sent": true,
                    "is_verified": true,
                    "verification_code": "_null_jOePj2i769OQ4XsFPihlAVpH6RGN_idjsycxU6-WfRo",
                    "balance": 0,
                    "created_at": "2025-07-19T11:34:32.928150+07:00",
                    "updated_at": "2025-07-20T11:23:13.016496+07:00"
                }
            ]
        ```
        """
        user: U | AnonymousUser = request.user
        if (
            pk
            and user.__getattribute__("is_active")
            and (
                user.__getattribute__("is_staff")
                or user.__getattribute__("id") == int(pk)
            )
        ):
            try:
                users_list = [view async for view in Users.objects.filter(pk=int(pk))]
                if len(users_list) == 0:
                    Response(
                        {"data": "'pk' is invalid"}, status=status.HTTP_401_UNAUTHORIZED
                    )
                    # Get - data
                serializer = await sync_for_async(UsersForSuperuserSerializer, user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as error:
                return Response(
                    {"data": error.args.__getitem__(0)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(
            {"data": "User or 'pk' is invalid"}, status=status.HTTP_401_UNAUTHORIZED
        )

    @swagger_auto_schema(
        operation_description="""
        Method: POST and the fixed pathname of url  '/api/auth/register/'
        Example PATHNAME: "/api/auth/register/"
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            title="BodyData",
            in_=openapi.IN_BODY,
            required=["username", "password"],
            properties={
                "username": openapi.Schema(
                    example="nH2qGiehvEXjNiYqp3bOVtAYv....", type=openapi.TYPE_STRING
                ),
                "password": openapi.Schema(
                    example="nH2qGiehvEXjNiYqp3bOVtAYv....", type=openapi.TYPE_STRING
                ),
            },
        ),
        responses={
            201: UserResponseSerializer200,
            401: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=["person"],
    )
    async def create(self, request: HttpRequest) -> type(Response):
        user = request.user
        data = request.data
        response = Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            # sync to async - user's checker on the duplicate
            users_list: list[Users.objects] = await asyncio.create_task(
                asyncio.to_thread(new_connection, data=data)
            )

        except Exception as error:
            # RESPONSE WILL SEND. CODE 500
            response.data = {"data": error.args}
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return response
        # Condition - If the length of the users_list has more zero, it's mean what user has a duplicate.
        # Response will be return 401.
        if not user.is_authenticated and len(users_list) == 0:
            try:
                password_hes = self.get_hash_password(data.get("password"))
                serializer = Async_UsersSerializer(data=data)
                # CHECK - VALID DATA
                await self.serializer_validate(serializer)
                serializer.validated_data["password"] = password_hes
                await serializer.asave()
                data: dict = dict(serializer.data).copy()
                # # RUN THE TASK - Update CACHE's USER -send id to the redis from celer's task
                task_postman_for_user_id.delay((data.__getitem__("id"),))
            except Exception as error:
                # RESPONSE WILL BE TO SEND. CODE 500
                response.data = {"data": error.args}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return response
            # RESPONSE WILL BE TO SEND. CODE 200
            response.data = {"data": "OK"}
            try:
                if serializer.data.__getitem__("id"):
                    user_id_list = [
                        view async for view in Users.objects.filter(pk=data["id"])
                    ]
            except Exception as error:
                return Response(
                    {"data": error.args}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            response.status_code = status.HTTP_201_CREATED
            try:
                # SEND MESSAGE TO THE USER's EMAIL
                send = signal_user_registered.send
                asyncio.create_task(
                    asyncio.to_thread(
                        send,
                        sender=self.create,
                        named=data,
                        isinstance=user_id_list.__getitem__(0),
                    )
                )
            except (AttributeError, Exception) as error:
                response.data = {"data": error.args.__getitem__(0)}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return response

        response.data = {"data": "User was created before."}
        return response

    @swagger_auto_schema(
        operation_description="""
            Method: POST and the fixed pathname of url  '/api/auth/register/0/login/'
            Example PATHNAME: "/api/auth/register/0/login"

            """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            title="BodyData",
            in_=openapi.IN_BODY,
            required=["username", "password"],
            properties={
                "username": openapi.Schema(
                    example="nH2qGiehvEXjNiYqp3bOVtAYv....", type=openapi.TYPE_STRING
                ),
                "password": openapi.Schema(
                    example="nH2qGiehvEXjNiYqp3bOVtAYv....", type=openapi.TYPE_STRING
                ),
            },
        ),
        responses={
            200: UsersSerializer,
            401: ErrorResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=["person"],
        manual_parameters=[
            openapi.Parameter(
                # https://drf-yasg.readthedocs.io/en/stable/custom_spec.html?highlight=properties
                name="x-csrftoken",
                title="csr-ftoken",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                example={"x-csrftoken": "nH2qGiehvEXjNiYqp3bOVtAYv...."},
            )
        ],
    )
    async def login(self, request: HttpRequest, pk=0) -> HttpResponse:
        """
        "/api/auth/register/0/login"
        This method is used the user's login and IP ADDRESS of client.
        Here, If we have the object of user , it means we will  get token objects for user.
        "token_access" - it is general token of user for access to the service.
        "token_refresh" - it is token for refresh the access token.
        :param request:
        :param pk: not used. It is just for URL.
        :return: ```js
             {"data":[
                    {
                        "token_access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "live_time": 360,
                    },
                    {
                        "token_refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "live_time": 786521,
                    },
                ]}
                ````
        """
        user: U = request.user
        data: UserData = request.data
        valid_password: None | object = None
        try:
            # Validators
            valid_username = self.validate_username(data.get("username"))
            valid_password = self.validate_password(data.get("password"))
        except (AttributeError, TypeError, Exception) as error:
            return Response(
                {"data": " Data type is not validate: %s" % error.args},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not user.is_active and valid_username and valid_password:
            valid_username = data.get("username").split().__getitem__(0)
            valid_password = data.get("password").split().__getitem__(0)

            # Get hash password of user
            hash_password = self.get_hash_password(valid_password)
            # Check exists of user to the both db
            client = RedisOfPerson()
            users_list: List[dict] = []
            # 1/2 db
            async for key_one in iterator_get_person_cache(client):
                caches_user = await client.get(key_one)
                # Check the username
                if (
                    caches_user
                    and isinstance(caches_user, dict)
                    and caches_user.__getitem__("username") == valid_username
                ):
                    users_list.append(caches_user)
                    continue
            await client.close()

            if len(users_list) == 0:
                # 2 /2 db
                users_list: List[U] = [
                    view async for view in Users.objects.filter(username=valid_username)
                ]
            if len(users_list) == 0:
                return Response(
                    {"data": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )

            user_one = users_list.__getitem__(0)
            response = Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            # Check password of user
            if type(users_list) == List[U]:
                if not (user_one.__getattribute__("password") == hash_password):
                    log.error("Invalid password")
                    return response
            # check a password
            if not (user_one.__getitem__("password") == hash_password):
                log.error("Invalid password")
                return response
            # RUN THE TASK - Update CACHE's USER
            task_user_login.apply_async(
                kwargs={"user_id": user_one.__getattribute__("id")}
            )
            # GET AUTHENTICATION (USER SESSION) IN DJANGO
            # user activation
            user = await sync_for_async(
                authenticate, request, username=valid_username, password=valid_password
            )

            if user is not None:
                await sync_for_async(login, request, user)
            else:
                return Response(
                    {"data": "User not founded"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            try:

                # GET ACCESS TOKENS
                accesstoken = AccessToken(user)
                tokens = await accesstoken.async_token()
                # ИЗМЕНИТЬ ВРЕМЯ
                current_time = datetime.now()
                access_time = (SIMPLE_JWT.__getitem__("ACCESS_TOKEN_LIFETIME")).seconds
                refresh_time = (
                    SIMPLE_JWT.__getitem__("REFRESH_TOKEN_LIFETIME") + current_time
                ).timestamp() - time.time()

            except Exception as ex:
                return Response({"data": ex.args}, status=status.HTTP_401_UNAUTHORIZED)
            try:
                """ACCESS TOKEN BASE64"""
                access_binary = Binary()
                access_base64_str = access_binary.object_to_binary(tokens.access_token)
                access_result = access_binary.str_to_binary(access_base64_str)
                """ REFRESH TOKEN BASE64"""
                reffresh_binary = Binary()
                reffresh_base64_str = reffresh_binary.object_to_binary(tokens)
                reffresh_result = reffresh_binary.str_to_binary(reffresh_base64_str)
                return JsonResponse(
                    {
                        "data": [
                            {
                                "token_access": access_result,
                                "live_time": access_time,
                            },
                            {
                                "token_refresh": reffresh_result,
                                "live_time": refresh_time,
                            },
                        ]
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as ex:
                return Response(
                    {"data": ex.args.__getitem__(0)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(
            {"data": "User was login before "}, status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        operation_description="""
                    Method: PARCH and the fixed pathname of url  '/api/auth/register/<int:pk>/login/'
                    Example PATHNAME: "/api/auth/register/83/login"

                    """,
        responses={
            status.HTTP_200_OK: "OK",
            200: ErrorResponseSerializer,
            400: "Anonymous user",
            401: ErrorResponseSerializer,
        },
        # auto_schema=None,
        tags=["person"],
        manual_parameters=[
            # https://drf-yasg.readthedocs.io/en/stable/drf_yasg.html?highlight=type_int#module-drf_yasg.openapi
            openapi.Parameter(
                required=True,
                name="id",
                example=12,
                in_=openapi.IN_PATH,
                description="This is user's index  from 'auth/register/<int:pk>/login/'",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                required=True,
                name="AccessToken",
                example="nH2qGiehvEXjNiYqp3bOVtAYv....",
                in_=openapi.IN_HEADER,
                description="This token has a prefix. It's 'Bearer ' - beginning of token. Example: 'Bearer gASVKAEAAAAAAACM...'",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                required=True,
                name="x-csrftoken",
                example="dsdWeweTwqwiehvdEXjNiYqp3bOVtAYv....",
                in_=openapi.IN_HEADER,
                description="""
                'AccessToken' It's key from the header of request.
                'csrftoken' token need have to the request.cookie.
                A csrftoken, you can get by API: 'api/auth/csrftoken/' and the method 'GET'.
                """,
                type=openapi.TYPE_STRING,
            ),
        ],
    )
    async def logout(self, request: type(HttpRequest), pk=0) -> HttpResponse:
        """
        logout
           "/api/auth/register/<int:pk>/logout"

           Here, If we have the object of user , it means we will  get token objects from the request.
           "token_access" - it is general token of user for access to the service.
           "token_refresh" - it is token for refresh the access token.

           :param request:
           :param ing pk: Index of user for logout.
           :return: ```json
                    "staus":200
                   ````
                   Redirect to the main page.
        """
        user: U | AnonymousUser = request.user
        if user.is_active:
            try:
                # GET ACCESS TOKENS
                accesstoken = AccessToken()
                user = (await accesstoken.get_user_from_token(request)).__getitem__(0)
                user.is_active = False
                await user.asave()
                response = redirect("person_app.register")
                response.status_code = status.HTTP_200_OK
                response.delete_cookie("token_access")
                response.delete_cookie("token_refresh")
                return response
            except Exception:
                return Response(
                    {"data": "User has invalid"}, status=status.HTTP_401_UNAUTHORIZED
                )

        response = redirect("person_app.register")
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response

    @staticmethod
    def validate_username(value: str) -> None | object:
        regex = re.compile(r"(^[a-zA-Z]\w{3,50}_{0,2})[^_]")
        return regex.match(value)

    @staticmethod
    def validate_password(value: str) -> None | object:
        regex = re.compile(r"([\w%]{9,255})")
        return regex.match(value)

    @staticmethod
    def get_hash_password(password: str) -> str:
        """
        This method for hashing user password.
        :param password: Password of user before hashing (from request)
        :return: password hashed
        """
        try:
            # HASH PASSWORD OF USER
            hash = Hasher()
            salt = SECRET_KEY_DJ.replace("$", "/")
            hash_password = hash.hashing(password, salt)
            return hash_password
        except Exception as error:
            raise ValueError(error)

    @staticmethod
    async def serializer_validate(serializer):
        is_valid = await asyncio.create_task(asyncio.to_thread(serializer.is_valid))
        if not is_valid:
            raise serializers.ValidationError(serializer.errors)
