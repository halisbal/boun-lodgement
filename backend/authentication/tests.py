from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from .models import User
from constants import UserRoles, ALLOWED_EMAILS

User = get_user_model()


class AuthViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.auth_url = reverse("authentication:auth")
        self.user_data = {"email": "test@example.com", "password": "testpassword123"}
        ALLOWED_EMAILS.append(self.user_data["email"])  # Ensure email is allowed

    def test_create_user(self):
        response = self.client.post(self.auth_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_invalid_email(self):
        invalid_data = {"email": "invalid@example.com", "password": "testpassword123"}
        response = self.client.post(self.auth_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MeViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123",
        )
        self.token = Token.objects.create(user=self.user)
        self.me_url = reverse("authentication:me")

    def test_get_me_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_get_me_unauthenticated(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="adminpassword123",
            role=UserRoles.ADMIN,
        )
        self.user = User.objects.create_user(
            username="regularuser", email="user@example.com", password="userpassword123"
        )
        self.token = Token.objects.create(user=self.admin_user)
        self.user_url = reverse("authentication:user-list")

    def test_list_users_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get(self.user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_as_non_admin(self):
        non_admin_token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + non_admin_token.key)
        response = self.client.get(self.user_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_user_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        edit_url = reverse("authentication:user-edit", args=[self.user.id])
        response = self.client.patch(edit_url, {"first_name": "NewName"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "NewName")

    def test_edit_user_as_non_admin(self):
        non_admin_token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + non_admin_token.key)
        edit_url = reverse("authentication:user-edit", args=[self.user.id])
        response = self.client.patch(edit_url, {"first_name": "NewName"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
