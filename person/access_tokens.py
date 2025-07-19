from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from person.models import Users
from typing import Optional, Dict


class AccessToken:
    def __init__(self, user_object: Optional[Users]):
        self.user_object = user_object

    async def async_token(self):
        """
        This is method for getting token for user.
        :param user_object: This is a user's object for a which will be token generating \
        :return: this dictionary with 4 values
        :return: {
                {"token_access": "< access_token >", "live_time": "< life_time_of_token >"},
                {"token_refresh": "< refresh_token >", "live_time": "< life_time_of_token >"}
            }
        """

        tokens = await self.__async_generate_jwt_token(self.user_object)
        return tokens

    @staticmethod
    async def __async_generate_jwt_token(
        user_object: Optional[Users],
    ) -> {Dict[str, str]}:
        """
            Only, after registration user we will be generating token for \
            user through 'rest_framework_simplejwt.serializers.TokenObtainPairSerializer'
            This is a generator token of user.\
            The 'SIMPLE_JWT' is variable from the project's 'settings.py' file.\
            @SIMPLE_JWT.ACCESS_TOKEN_LIFETIME this is minimum quantity for life of token\
             It is for the access.\
            @REFRESH_TOKEN_LIFETIME this is maximum quantity fro life token. \
            It is for the refresh.
            'TokenObtainPairSerializer' it has own db/
            :return:
        """
        """TIME TO THE LIVE TOKEN"""
        # dt = datetime.datetime.now() + datetime.timedelta(days=1)
        """GET TOKEN"""
        try:
            token = TokenObtainPairSerializer.get_token(user_object)
            token["name"] = (lambda: user_object.username)()
            return token
        except Exception as ex:
            raise ValueError("Value Error: %s" % ex)
