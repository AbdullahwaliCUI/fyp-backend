import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from app.models import Supervisor, CustomUser


@pytest.mark.django_db
class TestSupervisorLoginAPIView:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def supervisor_user(self):
        user = CustomUser.objects.create(
            username="supervisor1",
            email="supervisor@example.com",
            password=make_password("securepassword123"),
            user_type="supervisor",
        )
        Supervisor.objects.create(user=user, supervisor_id="SUP123")
        return user

    @patch("app.views.get_tokens_for_user")  # Adjust import path accordingly
    def test_login_success(self, mock_get_tokens, api_client, supervisor_user):
        mock_get_tokens.return_value = {
            "access": "mock-access-token",
            "refresh": "mock-refresh-token",
        }

        url = reverse("supervisor-login")
        data = {"email": supervisor_user.email, "password": "securepassword123"}

        response = api_client.post(url, data)

        assert response.status_code == 200
        assert response.data == {
            "access": "mock-access-token",
            "refresh": "mock-refresh-token",
        }
        mock_get_tokens.assert_called_once_with(supervisor_user)

    def test_login_invalid_password(self, api_client, supervisor_user):
        url = reverse("supervisor-login")
        data = {"email": supervisor_user.email, "password": "wrongpassword"}

        response = api_client.post(url, data)

        assert response.status_code == 401
        assert response.data["message"] == "Invalid credentials"

    def test_login_nonexistent_user(self, api_client):
        url = reverse("supervisor-login")
        data = {"email": "nonexistent@example.com", "password": "somepassword"}

        response = api_client.post(url, data)

        assert response.status_code == 401
        assert response.data["message"] == "Invalid credentials"

    def test_login_invalid_serializer_data(self, api_client):
        url = reverse("supervisor-login")

        # Missing email
        response = api_client.post(url, {"password": "somepassword"})
        assert response.status_code == 400
        assert "email" in response.data

        # Missing password
        response = api_client.post(url, {"email": "supervisor@example.com"})
        assert response.status_code == 400
        assert "password" in response.data

        # Empty data
        response = api_client.post(url, {})
        assert response.status_code == 400
        assert "email" in response.data
        assert "password" in response.data
