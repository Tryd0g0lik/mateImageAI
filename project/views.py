from django.http import JsonResponse
from django.middleware.csrf import get_token
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

# @swagger_auto_schema(operation_description="GET /api/auth/csrftoken/", tags=["person"],)
# def csrf_token(request, *args, **kwargs):
#
#     if request.method == "GET":
#         token = get_token(request)
#         response = JsonResponse({'csrfToken': token})
#         response.status_code = status.HTTP_201_CREATED
#         return response
#     response = Response(status=status.HTTP_400_BAD_REQUEST)
#     return response


class CSRFTokenView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Получить CSRF токен",
        tags=["Аутентификация"],
        responses={
            200: openapi.Response(
                description="CSRF токен",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"csrfToken": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
            400: "NOT OK",
        },
    )
    def get(self, request, *args, **kwargs):
        if request.method == "GET":
            token = get_token(request)
            response = JsonResponse({"csrfToken": token})
            response.status_code = status.HTTP_201_CREATED
            return response
        response = Response(status=status.HTTP_400_BAD_REQUEST)
        response.data = "NOT OK"
        return response
