import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from app.models import Student

User = get_user_model()

@pytest.mark.django_db
class TestStudentLoginView:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.login_url = reverse("student-login")

        # Create user and student
        self.password = "strongpassword123"
        self.user = User.objects.create_user(
            username="teststudent",
            email="student@example.com",
            password=self.password,
            user_type="student"
        )

        self.student = Student.objects.create(
            user=self.user,
            registration_no="REG123456",
            department="CS",
            semester="semester_6",
            batch_no="2021"
        )

    def test_login_success(self):
        data = {
            "registration_no": "REG123456",
            "password": self.password
        }
        response = self.client.post(self.login_url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "expire_time" in response.data

    def test_login_invalid_password(self):
        data = {
            "registration_no": "REG123456",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, data, format="json")
        assert response.status_code == 401
        assert response.data["message"] == "Invalid credentials"

    def test_login_invalid_registration_no(self):
        data = {
            "registration_no": "WRONG123",
            "password": self.password
        }
        response = self.client.post(self.login_url, data, format="json")
        assert response.status_code == 401
        assert response.data["message"] == "Invalid credentials"

    def test_login_missing_registration_no(self):
        data = {
            "password": self.password
        }
        response = self.client.post(self.login_url, data, format="json")
        assert response.status_code == 400
        assert "registration_no" in response.data

    def test_login_missing_password(self):
        data = {
            "registration_no": "REG123456"
        }
        response = self.client.post(self.login_url, data, format="json")
        assert response.status_code == 400
        assert "password" in response.data

    def test_login_empty_fields(self):
        data = {
            "registration_no": "",
            "password": ""
        }
        response = self.client.post(self.login_url, data, format="json")
        assert response.status_code == 400
        assert "registration_no" in response.data
        assert "password" in response.data

    def test_login_non_json_format(self):
        # Send incorrect content-type
        response = self.client.post(self.login_url, "notjson", content_type="text/plain")
        assert response.status_code == 415
