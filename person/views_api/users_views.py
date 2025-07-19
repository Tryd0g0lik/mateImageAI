import time
from datetime import datetime

from asgiref.sync import sync_to_async

from drf_yasg import openapi

from dotenv_ import SECRET_KEY_DJ
from django.contrib.auth import authenticate, login
from django.http import JsonResponse

# from django.utils.translation import gettext_lazy as _
from person.access_tokens import AccessToken
from person.hasher import PasswordHasher
from person.models import Users
from person.apps import signal_user_registered
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from adrf.viewsets import ViewSet
from rest_framework.decorators import permission_classes
from person.serializers import (
    UsersSerializer,
    UsersRequestLoginSerializer,
    TokenReqponseLoginSerializer200,
)
from drf_yasg.utils import swagger_auto_schema
from person.serializers import (
    UserResponseSerializer200,
    ErrorResponseSerializer,
)
from project.settings import SECRET_KEY, SIMPLE_JWT
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
        request_body=UsersSerializer,
        query_serializer=UsersSerializer,
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
        request_body=UsersRequestLoginSerializer,
        responses={
            200: TokenReqponseLoginSerializer200,
            401: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=["person"],
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

    @swagger_auto_schema(
        operation_description="""
                Method: POST and the fixed pathname of url  '/api/auth/register/<int:pk>/login/'
                Example PATHNAME: "/api/auth/register/83/login"

                """,
        request_body=UsersRequestLoginSerializer,
        responses={
            status.HTTP_200_OK: TokenReqponseLoginSerializer200,
            401: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        # auto_schema=None,
        tags=["person"],
        manual_parameters=[
            # https://drf-yasg.readthedocs.io/en/stable/drf_yasg.html?highlight=type_int#module-drf_yasg.openapi
            openapi.Parameter(
                name="id",
                in_=openapi.IN_PATH,
                description="This is user's index  from 'auth/register/<int:id>/login/'",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    async def logout(self, request, pk=0) -> type(Response):
        """
        logout
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

    @staticmethod
    def get_hash_password(password: str) -> str:
        """
        This method for hashing user password.
        :param password: Password of user before hashing (from request)
        :return: password hashed
        """
        try:
            # HASH PASSWORD OF USER
            hash = PasswordHasher()
            salt = SECRET_KEY_DJ.replace("$", "/")
            hash_password = hash.hasher(password, salt)
            return hash_password
        except Exception as error:
            raise ValueError(error)
