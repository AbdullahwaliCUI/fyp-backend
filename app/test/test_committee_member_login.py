import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from app.models import CommitteeMember, CustomUser, CommitteeMemberPanel


@pytest.mark.django_db
class TestCommitteeMemberLoginAPIView:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def panel(self):
        return CommitteeMemberPanel.objects.create(name="Test Panel")

    @pytest.fixture
    def committee_user(self, panel):
        user = CustomUser.objects.create(
            username="committeemember",
            email="member@example.com",
            password=make_password("securepassword123"),
            user_type="committee",
        )
        CommitteeMember.objects.create(user=user, committee_id="COM123", panel=panel)
        return user

    def test_login_success(self, api_client, committee_user):
        url = reverse("committee-member-login")
        data = {"email": committee_user.email, "password": "securepassword123"}

        response = api_client.post(url, data)

        assert response.status_code == 200
        assert (
            "access" in response.data
        )  # assuming get_tokens_for_user returns a token dict with 'access' key
        assert "refresh" in response.data

    def test_login_invalid_password(self, api_client, committee_user):
        url = reverse("committee-member-login")
        data = {"email": committee_user.email, "password": "wrongpassword"}

        response = api_client.post(url, data)

        assert response.status_code == 401
        assert response.data["message"] == "Invalid credentials"

    def test_login_nonexistent_user(self, api_client):
        url = reverse("committee-member-login")
        data = {"email": "nonexistent@example.com", "password": "doesntmatter"}

        response = api_client.post(url, data)

        assert response.status_code == 401
        assert response.data["message"] == "Invalid credentials"

    def test_login_invalid_serializer_data(self, api_client):
        url = reverse("committee-member-login")

        # Missing email
        response = api_client.post(url, {"password": "somepassword"})
        assert response.status_code == 400
        assert "email" in response.data

        # Missing password
        response = api_client.post(url, {"email": "member@example.com"})
        assert response.status_code == 400
        assert "password" in response.data

        # Empty data
        response = api_client.post(url, {})
        assert response.status_code == 400
        assert "email" in response.data
        assert "password" in response.data
