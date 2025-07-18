from rest_framework import serializers
from person.models import Users


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = "__all__"


class UserResponseSerializer(serializers.Serializer):
    data = serializers.CharField(default="OK")


class ErrorResponseSerializer(serializers.Serializer):
    data = serializers.CharField()
    error = serializers.CharField(required=False)
