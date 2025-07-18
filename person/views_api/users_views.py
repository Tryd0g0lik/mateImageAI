from dotenv_ import SECRET_KEY_DJ
from django.utils.decorators import method_decorator
from person.hasher import PasswordHasher
from person.models import Users
from person.apps import signal_user_registered
from rest_framework import serializers, status
from rest_framework.response import Response

from adrf.viewsets import ViewSet

from person.serializers import UsersSerializer
from drf_yasg.utils import swagger_auto_schema


def serializer_validate(serializer):
    is_valid = serializer.is_valid()
    if not is_valid:
        raise serializers.ValidationError(serializer.errors)


class UserViews(ViewSet):

    @method_decorator(
        swagger_auto_schema(
            operation_description="Создание нового пользователя",
            request_body=UsersSerializer,
            responses={
                201: UsersSerializer,
                401: {
                    "description": "Неавторизованный запрос или пользователь уже существует"
                },
                500: {"description": "Внутренняя ошибка сервера"},
            },
            tags=["Users"],
        )
    )
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
                response.status = status.HTTP_201_CREATED
                # SEND MESSAGE TO THE USER's EMAIL
                user_ = Users.objects.get(pk=serializer.data["id"])
                signal_user_registered.send(
                    sender=self.create, data=data, isinstance=user_
                )
            except Exception as error:
                # RESPONSE WILL BE TO SEND. CODE 401
                response.data = {"data": error}
                response.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            finally:
                return response

        response.data = {"data": "User was created before."}
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
            hash = PasswordHasher()
            salt = SECRET_KEY_DJ.replace("$", "/")
            hash_password = hash.hasher(password, salt)
            return hash_password
        except Exception as error:
            raise ValueError(error)
