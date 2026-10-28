from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.http import JsonResponse
from rest_framework.response import Response
from .serializers import UserSerializer
import datetime


class LoginView(APIView):
    permission_classes = [AllowAny]  # 允许未登录用户访问

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)

            return Response({
                "user": UserSerializer(user).data,
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            })
            # response = JsonResponse({"message": "Login successful", "access_token": str(refresh.access_token)})
            # response.set_cookie(
            #     'refresh_token',
            #     refresh,
            #     httponly=True,
            #     secure=True,  # 如果使用 HTTPS
            #     max_age=datetime.timedelta(days=7)  # 设置 cookie 的过期时间
            # )
            # return response
        return Response({"error": "用户名或密码错误"}, status=status.HTTP_401_UNAUTHORIZED)
