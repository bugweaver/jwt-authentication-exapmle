from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User, RefreshToken
from .serializers import (
    UserSerializer,
    RegistrationSerializer,
    LoginSerializer,
    RefreshSerializer,
    LogoutSerializer,
)
from .authentication import generate_access_token, generate_refresh_token


class RegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = authenticate(email=email, password=password)

        if user:
            access_token = generate_access_token(user)
            refresh_token = generate_refresh_token(user)
            return Response(
                data={"access_token": access_token, "refresh_token": refresh_token},
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
        )


class RefreshView(generics.GenericAPIView):
    serializer_class = RefreshSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh_token"]

        try:
            refresh_token_obj = RefreshToken.objects.get(token=refresh_token)
            if refresh_token_obj.expires_at < timezone.now():
                return Response(
                    data={"message": "Refresh token has expired"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = refresh_token_obj.user
            access_token = generate_access_token(user)
            new_refresh_token = generate_refresh_token(user)
            refresh_token_obj.delete()
            return Response(
                data={"access_token": access_token, "refresh_token": new_refresh_token},
                status=status.HTTP_200_OK,
            )

        except RefreshToken.DoesNotExist:
            return Response(
                data={"message": "Invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    http_method_names = ["post", "options"]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh_token"]

        try:
            refresh_token_token_obj = RefreshToken.objects.get(token=refresh_token)
            refresh_token_token_obj.delete()
            return Response(
                data={"success": "User logged out"},
                status=status.HTTP_200_OK,
            )
        except RefreshToken.DoesNotExist:
            return Response(
                data={"message": "Invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserMeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
