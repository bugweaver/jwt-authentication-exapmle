import uuid

import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from rest_framework import authentication, exceptions
from constance import config
from .models import User, RefreshToken


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_data = authentication.get_authorization_header(request)
        if not auth_data:
            return None

        prefix = auth_data.decode("utf-8").split(" ")[0]
        token = auth_data.decode("utf-8").split(" ")[1]

        if prefix.lower() != "bearer":
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.DecodeError as e:
            raise exceptions.AuthenticationFailed(f"Your token is invalid. Error: {e}")
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Your token has expired")

        try:
            user_id = payload["user_id"]
            user = User.objects.get(pk=user_id)
            return user, token
        except KeyError:
            raise exceptions.AuthenticationFailed("Token payload is invalid")
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("User not found")


def generate_access_token(user):
    payload = {
        "user_id": user.id,
        "exp": datetime.now(timezone.utc)
        + timedelta(seconds=config.ACCESS_TOKEN_LIFETIME_SECONDS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def generate_refresh_token(user):
    while True:
        token = uuid.uuid4()
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=config.REFRESH_TOKEN_LIFETIME_DAYS
        )

        if not RefreshToken.objects.filter(token=token).exists():
            refresh_token = RefreshToken.objects.create(
                user=user, token=token, expires_at=expires_at
            )
            return refresh_token.token
