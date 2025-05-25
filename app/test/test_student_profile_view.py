import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models import Student, Group
from app.models import SupervisorOfStudentGroup

User = get_user_model()

@pytest.mark.django_db
class TestStudentProfileView:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def student_user(self):
        return User.objects.create_user(username="student1", password="strongpass123", user_type="student")

    @pytest.fixture
    def student(self, student_user):
        return Student.objects.create(
            user=student_user,
            registration_no="REG123",
            department="CS",
            semester="semester_6",
            batch_no="2021"
        )

    @pytest.fixture
    def supervisor_group(self, student):
        group = Group.objects.create(student_1=student, status="accepted")
        return SupervisorOfStudentGroup.objects.create(group=group, status="accepted")

    @pytest.fixture
    def groupmate_group(self, student):
        # Create second student for groupmate
        mate_user = User.objects.create_user(username="student2", password="strongpass123", user_type="student")
        mate = Student.objects.create(
            user=mate_user,
            registration_no="REG456",
            department="CS",
            semester="semester_6",
            batch_no="2021"
        )
        return Group.objects.create(student_1=student, student_2=mate, status="accepted")

    def test_student_profile_authenticated(self, api_client, student_user, student):
        """Should return student profile when authenticated"""
        api_client.force_authenticate(user=student_user)
        url = reverse("student-profile")
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data["registration_no"] == "REG123"
        assert response.data["user"]["username"] == "student1"
        assert response.data["group_id"] is None
        assert response.data["groupmate_id"] is None

    def test_student_profile_with_group_ids(self, api_client, student_user, student, supervisor_group, groupmate_group):
        """Should return group_id and groupmate_id if exists and status accepted"""
        api_client.force_authenticate(user=student_user)
        url = reverse("student-profile")
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data["group_id"] == supervisor_group.id
        assert response.data["groupmate_id"] == groupmate_group.id

    def test_student_profile_unauthenticated(self, api_client):
        """Should reject unauthenticated access"""
        url = reverse("student-profile")
        response = api_client.get(url)

        assert response.status_code == 401  # Unauthorized
        assert "credentials" in str(response.data).lower()

    def test_student_profile_user_without_student_profile(self, api_client):
        """Should raise error if authenticated user has no Student profile"""
        user = User.objects.create_user(username="other_user", password="abc123", user_type="student")
        api_client.force_authenticate(user=user)
        url = reverse("student-profile")
        response = api_client.get(url)

        assert response.status_code == 500 or response.status_code == 404
