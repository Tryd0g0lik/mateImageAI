import time
import asyncio
import re
from contextlib import nullcontext
from datetime import datetime
from collections.abc import Callable
from typing import (Any, TypedDict,
                    NotRequired,
                    Generic, List)
from urllib.request import Request

from colorful.terminal import TRUE_COLORS
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.password_validation import validate_password
from django.db import connection, transaction
from django.db.models.expressions import result
from django.middleware.csrf import get_token
from asgiref.sync import sync_to_async
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_exempt

from drf_yasg import openapi
from rest_framework_simplejwt.utils import aware_utcnow
from twisted.internet.defer import execute
from twisted.web.http import responses

from dotenv_ import SECRET_KEY_DJ, POSTGRES_DB

# from django.utils.translation import gettext_lazy as _
from person.access_tokens import AccessToken
from person.hasher import Hasher
from person.interfaces import U
from person.models import Users
from person.apps import signal_user_registered
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from adrf.viewsets import ViewSet
from rest_framework.decorators import permission_classes
from person.serializers import (
    UsersSerializer,
    TokenReqponseLoginSerializer200,
    UsersForSuperuserSerializer,
    Async_UsersSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from person.serializers import (
    UserResponseSerializer200,
    ErrorResponseSerializer,
)
from project.settings import SIMPLE_JWT
from person.binaries import Binary
import logging
from logs import configure_logging
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)
configure_logging(logging.INFO)

class UserData(TypedDict):
    """
    Type for register, login, etc.
    """
    username: str
    password: str
    email: NotRequired[str]



async def sync_for_async(fn: Callable[[Any], Any], *args, **kwargs):
    return await asyncio.create_task(asyncio.to_thread(fn, *args, **kwargs))

async def serializer_validate(serializer):
    is_valid = await asyncio.create_task(asyncio.to_thread(serializer.is_valid))
    # is_valid = await serializer.is_valid()
    if not is_valid:
        raise serializers.ValidationError(serializer.errors)


def new_connection(data) -> list:
    """
    new user cheks on the duplicate
    :param data:
    :return:
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT * FROM %s WHERE username == '%s' AND email == '%s';"""
            % (POSTGRES_DB, data.get("username"), data.get("email"))
        )
        resp_list = cursor.fetchall()
        users_list = [view for view in resp_list]
    return users_list


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
    def list(self, request) -> type(Response):
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
        user = request.user
        if user.is_active and user.is_staff:
            try:
                queryset = Users.objects.all()
                serializer = UsersForSuperuserSerializer(queryset, many=True)
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
        if pk and user.is_active and (user.is_staff or user.id == int(pk)):
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
                log.info("RETRIEVE, ERROR: %s:" % error.args)
                return Response(
                    {"data": error.args}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
        # users_list = Users.objects.filter(username=data.get("username"))
        # users_list = Users.objects.filter(email=data.get("email"))
        if not user.is_authenticated and len(users_list) == 0:
            try:
                password = self.get_hash_password(data.get("password"))
                serializer = Async_UsersSerializer(data=data)
                # CHECK - VALID DATA
                await serializer_validate(serializer)
                serializer.validated_data["password"] = password
                await serializer.asave()
            except Exception as error:
                # RESPONSE WILL BE TO SEND. CODE 500
                response.data = {"data": error.args}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return response
            # RESPONSE WILL BE TO SEND. CODE 200
            response.data = {"data": "OK"}
            user_id_list = [
                view async for view in Users.objects.filter(pk=serializer.data["id"])
            ]
            response.status_code = status.HTTP_201_CREATED
            try:
                # SEND MESSAGE TO THE USER's EMAIL
                send = signal_user_registered.send
                asyncio.create_task(
                    asyncio.to_thread(
                        send, sender=self.create, named=data, isinstance=user_id_list[0]
                    )
                )
            except (AttributeError, Exception) as error:
                response.data = {"data": error.args}
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
        log.info("TEST 1 USER: %s" % user)
        valid_password: None | object = None
        try:
            # Validators
            valid_username = self.validate_username(data.get("username"))
            valid_password = self.validate_password(data.get("password"))
        except(AttributeError, TypeError, Exception) as error:
            return Response(
                {"data": ' Data type is not validate: %s' % error.args}, status=status.HTTP_404_NOT_FOUND
            )
        if not user.is_active and valid_username and valid_password:
            valid_username = data.get("username").split()[0]
            valid_password = data.get("password").split()[0]
            log.info("USER USERNAME: %s" % valid_username)

            # Get hash password of user
            hash_password = self.get_hash_password(valid_password)
            # Check exists of user
            users_list: List[U] = [view async for view in Users.objects.filter(username=valid_username)]
            if len(users_list) == 0:
                return Response(
                    {"data": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )
            user_one = users_list[0]
            log.info("USER OF DB: %s" % user_one)
            if not user_one:
                return Response(
                    {"data": "User not founded"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            # check a password
            if not user_one.password == hash_password:
                log.error("Invalid password")
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            # Get user's data
            user_one.date_joined = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%u")
            user_one.is_active = True
            # Save user 1/2
            try:
                await user_one.asave()
            except (TypeError, Exception) as error:
                return Response(
                    {"error": error.args[0]},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            # GET AUTHENTICATION (USER SESSION) IN DJANGO
            user = await sync_for_async(authenticate,request, username=valid_username, password=valid_password)
            if user is not None:
                await sync_for_async(login, request, user)
            else:
                return Response(
                    {"data": "User not founded"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            try:
                user_one.last_login = datetime.now()
                # Save user 2/2
                try:
                    await user_one.asave()
                except (TypeError, Exception) as error:
                    return Response(
                        {"error": error.args[0]},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
                # GET ACCESS TOKENS
                accesstoken = AccessToken(user)
                tokens = await accesstoken.async_token()
                # ИЗМЕНИТЬ ВРЕМЯ
                current_time = datetime.now()
                access_time = (SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]).seconds
                refresh_time = (
                    SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] + current_time
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
                    {"data": ex.args}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
    async def logout(self, request: type(HttpRequest), pk=0) -> type(Response):
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
        user = request.user
        if user.is_active:
            try:
                # GET ACCESS TOKENS
                accesstoken = AccessToken()
                user = await accesstoken.get_user_from_token(request)
                user.is_active = False
                await sync_to_async(user.save)()
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
    def validate_username(value: str) -> None|object:
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

