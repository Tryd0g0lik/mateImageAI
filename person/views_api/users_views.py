import time
from contextlib import nullcontext
from datetime import datetime
from tkinter.scrolledtext import example

from colorful.terminal import TRUE_COLORS
from django.middleware.csrf import get_token
from asgiref.sync import sync_to_async
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from drf_yasg import openapi
from twisted.web.http import responses

from dotenv_ import SECRET_KEY_DJ
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpRequest

# from django.utils.translation import gettext_lazy as _
from person.access_tokens import AccessToken
from person.hasher import Hasher
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
)
from drf_yasg.utils import swagger_auto_schema
from person.serializers import (
    UserResponseSerializer200,
    ErrorResponseSerializer,
)
from project.settings import SIMPLE_JWT
from person.binaries import Binary


def serializer_validate(serializer):
    is_valid = serializer.is_valid()
    if not is_valid:
        raise serializers.ValidationError(serializer.errors)


class UserViews(ViewSet):

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
    @permission_classes([AllowAny])
    def create(self, request) -> type(Response):
        user = request.user
        data = request.data
        response = Response(status=status.HTTP_401_UNAUTHORIZED)
        # CHECK IF USER EXISTS
        user_name_list = Users.objects.filter(username=data.get("username"))
        user_email_list = Users.objects.filter(email=data.get("email"))
        if not user.is_authenticated and (
            not user_name_list.exists() or not user_email_list.exists()
        ):
            try:
                password = self.get_hash_password(request.data.get("password"))
                serializer = UsersSerializer(data=data)
                serializer_validate(serializer)
                serializer.validated_data["password"] = password
                serializer.save()
                # RESPONSE WILL BE TO SEND. CODE 200
                response.data = {"data": "OK"}
                response.status_code = status.HTTP_201_CREATED
                # SEND MESSAGE TO THE USER's EMAIL
                user_ = Users.objects.get(pk=serializer.data["id"])
                signal_user_registered.send(
                    sender=self.create, data=data, isinstance=user_
                )
            except Exception as error:
                # RESPONSE WILL BE TO SEND. CODE 401
                response.data = {"data": error}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            finally:
                return response

        response.data = {"data": "User was created before."}
        return response
        # 201: TokenResponseSerializer,

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
    async def login(self, request, pk=0) -> type(Response):
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
        user = request.user

        if not user.is_authenticated:
            password = request.data.get("password")
            login_user = request.data.get("username")

            # HASH PASSWORD OF USER
            hash_password = self.get_hash_password(request.data.get("password"))
            # CHECK EXISTS OF USER
            user_one_list = await sync_to_async(Users.objects.filter)(
                username=login_user, password=hash_password
            )
            user_one = await sync_to_async(user_one_list.first)()

            if not user_one:
                return Response(
                    {"data": "User not founded"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # GET USER DATA
            user_one.is_active = True
            # SAVE USER
            await sync_to_async(user_one.save)()
            # GET AUTHENTICATION (USER SESSION) IN DJANGO
            user = await sync_to_async(authenticate)(
                request, username=login_user, password=password
            )
            if user is not None:
                await sync_to_async(login)(request, user)
            else:
                return Response(
                    {"data": "User not founded"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            try:
                user_one.last_login = datetime.now()
                # SAVE USER
                await sync_to_async(user_one.save)()
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
