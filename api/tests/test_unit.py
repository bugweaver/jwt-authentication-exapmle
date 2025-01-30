import uuid

from django.test import TestCase

from api.models import RefreshToken, User
from api.authentication import generate_access_token, generate_refresh_token

from datetime import datetime, timezone


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword"
        )

    def test_generate_access_token(self):
        token = generate_access_token(self.user)
        self.assertIsInstance(token, str)

    def test_generate_refresh_token(self):
        token = generate_refresh_token(self.user)
        self.assertIsInstance(token, uuid.UUID)
        self.assertTrue(RefreshToken.objects.filter(token=token).exists())

    def test_generate_refresh_token_lifetime(self):
        refresh_token = generate_refresh_token(self.user)
        token_obj = RefreshToken.objects.get(token=refresh_token)
        self.assertGreater(token_obj.expires_at, datetime.now(timezone.utc))

    def test_create_user(self):
        user = User.objects.create_user(email="user@example.com", password="password")
        self.assertIsInstance(user, User)
