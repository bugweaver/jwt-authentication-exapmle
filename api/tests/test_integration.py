from django.urls import reverse

from api.models import User

from rest_framework import status
from rest_framework.test import APITestCase


class AuthIntegrationTests(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "password": "testpassword",
        }
        self.user = User.objects.create_user(**self.user_data)

    def login_and_get_token(self):
        url = reverse("login")
        response = self.client.post(url, self.user_data, format("json"))
        return response.data["access_token"]

    def test_registration(self):
        url = reverse("register")
        data = {"email": "newuser@example.com", "password": "newpassword"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], data["email"])
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_login(self):
        url = reverse("login")
        response = self.client.post(url, self.user_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)

    def test_login_invalid_credentials(self):
        url = reverse("login")
        data = {
            "email": "test@example.com",
            "password": "wrongpassword",
        }
        response = self.client.post(url, data, format("json"))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh(self):
        login_url = reverse("login")
        login_response = self.client.post(login_url, self.user_data, format("json"))
        refresh_token = login_response.data["refresh_token"]
        refresh_url = reverse("refresh")
        response = self.client.post(
            refresh_url, {"refresh_token": refresh_token}, format("json")
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)

    def test_refresh_invalid_token(self):
        refresh_url = reverse("refresh")
        response = self.client.post(
            refresh_url, {"refresh_token": "invalid_token"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        access_token = self.login_and_get_token()
        login_url = reverse("login")
        login_response = self.client.post(login_url, self.user_data, format("json"))
        refresh_token = login_response.data["refresh_token"]
        logout_url = reverse("logout")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        response = self.client.post(
            logout_url, {"refresh_token": refresh_token}, format("json")
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], "User logged out")

    def test_logout_invalid_token(self):
        logout_url = reverse("logout")
        response = self.client.post(
            logout_url, {"refresh_token": "invalid_token"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_me_authenticated(self):
        access_token = self.login_and_get_token()
        me_url = reverse("me")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        response = self.client.get(me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user_data["email"])

    def test_update_me_authenticated(self):
        access_token = self.login_and_get_token()
        me_url = reverse("me")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        data = {"username": "John Smith"}
        response = self.client.patch(me_url, data, format("json"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], data["username"])

    def test_get_me_unauthenticated(self):
        me_url = reverse("me")
        response = self.client.get(me_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
