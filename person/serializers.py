from asyncio import shield

from django.core.validators import MinValueValidator, MinLengthValidator
from rest_framework import serializers
from rest_framework import status
from person.models import Users
from django.utils.translation import gettext_lazy as _


# REGISTRATION
class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ["id", "username", "email", "password"]


# SWAGGER BELOW
# REGISTRATION AND LOGIN


# https://www.django-rest-framework.org/api-guide/fields/
class UserResponseSerializer200(serializers.Serializer):
    # data = serializers.CharField(default="OK")
    # status = serializers.IntegerField(default=200,)
    data = serializers.CharField(default="OK")
    status = serializers.IntegerField(
        default=200,
    )


# class UserResponseAccessSerialiser(serializers.ModelSerializer):


class ErrorResponseSerializer(serializers.Serializer):
    data = serializers.CharField()
    error = serializers.CharField(required=False, default=None)
    status_code = serializers.IntegerField(
        required=False, default=status.HTTP_401_UNAUTHORIZED
    )


# LOGIN - STATUS CODE 200
class UsersRequestLoginSerializer(serializers.Serializer):
    """
    This is data we need to get from the 'request.data'.
    :param str username:
    :param str password:
    """

    username = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(required=True, max_length=255)


class TokenSerializer200(serializers.Serializer):
    """
    This is we cheking the dictionary which contains only two rows.
    Three symbol is a min value for the 'property' line.
    :param str property: This a fixed key which contain one from two names. It's 'token_access' or 'token_refresh'.
    :param int live_time: Three symbol is a min value for tome life  of 'property'.
    Example:
        ````json
             {
               "token_access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
               "live_time": 360,
            }
            # or
          {
               "token_refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
               "live_time": ...,
           }
        ```
    """

    property = serializers.CharField(
        required=True,
        help_text=_(
            "This names - 'token_access' or 'token_refresh' must have this UNIQUE key."
        ),
        validators=[MinLengthValidator(3, message=_("Three symbol is a min value"))],
    )
    live_time = serializers.IntegerField(
        required=True,
        validators=[
            MinValueValidator(0, message=_("Zero is min value")),
        ],
    )


class TokenReqponseLoginSerializer200(serializers.Serializer):
    """
    :param dict data: Here contain the fixed key 'data', it's one key from more.
    Values,  from the 'data' key, is data type the list.
    :param int status: THis filed contains the status-code for http-response.
    Example:
    ```json
    {
        "data":[
           {
               "token_access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
               "live_time": 360,
           },
           {
               "token_refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
               "live_time": 786521,
           },
       ]
    }
    ```
    # "Ключ должен иметь имя 'token_access' или 'token_refresh'"
    """

    data = serializers.ListField(
        required=True, child=TokenSerializer200(), min_length=2, max_length=2
    )
    status = serializers.IntegerField(default=status.HTTP_200_OK)

    def validate_data(self, value):
        keys_list = []
        for item in value:
            if not ("token_access" in item or "token_refresh" in item):
                raise serializers.ValidationError(
                    "Каждый элемент должен содержать 'token_access' или 'token_refresh'"
                )
            if "live_time" not in item:
                raise serializers.ValidationError("Отсутствует 'live_time'")
            keys_list += list(item.keys())
        # 'token_access' in item or 'token_refresh'
        if (
            0 == keys_list.count("token_access") >= 2
            or 0 == keys_list.count("token_refresh") >= 2
        ):
            serializers.ValidationError(
                "В списке должны быить уникальные ключи: 'token_access' и 'token_refresh'."
            )
        return value
