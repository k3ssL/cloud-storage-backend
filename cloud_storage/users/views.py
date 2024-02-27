from django.contrib.auth import authenticate, login, get_user_model, logout
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import UserRegistrationSerializer, UserLoginSerializer


class UserRegistrationAPIView(CreateAPIView):
    def create(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            first_name = serializer.validated_data['first_name']
            last_name = serializer.validated_data['last_name']

            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            token, created = Token.objects.get_or_create(user=user)

            return Response({
                "success": True,
                "message": "Success",
                "token": token.key
            }, status=status.HTTP_200_OK)

        else:
            error_messages = {}
            for key, value in serializer.errors.items():
                error_messages[key] = [value[0]]
            return Response({
                "success": False,
                "message": error_messages
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class UserLoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            try:
                user = get_user_model().objects.get(email=email, password=password)
            except:
                error_messages = {}
                for key, value in serializer.errors.items():
                    error_messages[key] = [value[0]]

                return Response({
                    "success": False,
                    "message": error_messages or "Login failed"
                }, status=status.HTTP_401_UNAUTHORIZED)

            if user is not None:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)

                return Response({
                    "success": True,
                    "message": "Success",
                    "token": token.key
                }, status=status.HTTP_200_OK)

        error_messages = {}
        for key, value in serializer.errors.items():
            error_messages[key] = [value[0]]

        return Response({
            "success": False,
            "message": error_messages or "Login failed"
        }, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutAPIView(APIView):
    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            logout(request)

            return Response({
                "success": True,
                "message": "Logout"
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                "success": False,
                "message": 'Login Failed'
            }, status=status.HTTP_403_FORBIDDEN)