import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.mark.django_db
class TestChangePasswordView:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.url = reverse("change_password")

        self.old_password = "OldPassword123"
        self.new_password = "NewPassword456"

        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password=self.old_password,
            user_type="student",
        )

        # Generate JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def authenticate(self):
        """Helper to add token to client headers"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_change_password_success(self):
        self.authenticate()
        data = {"old_password": self.old_password, "new_password": self.new_password}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Password changed successfully"
        self.user.refresh_from_db()
        assert self.user.check_password(self.new_password)

    def test_change_password_wrong_old_password(self):
        self.authenticate()
        data = {"old_password": "WrongOldPassword", "new_password": self.new_password}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Old password is incorrect"

    def test_change_password_missing_old_password(self):
        self.authenticate()
        data = {"new_password": self.new_password}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "old_password" in response.data

    def test_change_password_missing_new_password(self):
        self.authenticate()
        data = {"old_password": self.old_password}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in response.data

    def test_change_password_empty_fields(self):
        self.authenticate()
        data = {"old_password": "", "new_password": ""}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "old_password" in response.data
        assert "new_password" in response.data

    def test_change_password_unauthenticated(self):
        # No token provided
        data = {"old_password": self.old_password, "new_password": self.new_password}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.data
