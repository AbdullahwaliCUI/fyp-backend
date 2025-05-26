import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models import (
    Student,
    Group,
    SupervisorOfStudentGroup,
    ProjectCategories,
    Project,
    Supervisor,
)

User = get_user_model()


@pytest.mark.django_db
class TestStudentProfileView:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.student_1 = Student.objects.create(
            user=User.objects.create(
                username="student1@gmail.com", email="student1@gmail.com"
            ),
            registration_no="1",
        )

        self.student_2 = Student.objects.create(
            user=User.objects.create(
                username="student2@gmail.com", email="student2@gmail.com"
            ),
            registration_no="2",
        )

        self.project_category = ProjectCategories.objects.create(
            category_name="Test Category"
        )

        self.project = Project.objects.create(project_category=self.project_category)

        self.student_group = Group.objects.create(
            student_1=self.student_1,
            student_2=self.student_2,
            project_category=self.project_category,
            status="accepted",
        )

        self.supervisor = Supervisor.objects.create(
            user=User.objects.create(
                username="supervisor1", email="supervisor1@gmail.com"
            )
        )

        self.supervisor_group = SupervisorOfStudentGroup.objects.create(
            group=self.student_group,
            status="accepted",
            created_by=self.student_1,
            project=self.project,
            supervisor=self.supervisor,
        )

    @pytest.fixture
    def api_client(self):
        return APIClient()

    def test_student_profile_authenticated(self, api_client):
        self.student_group.delete()
        api_client.force_authenticate(user=self.student_1.user)
        url = reverse("student-profile")
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data["registration_no"] == self.student_1.registration_no
        assert response.data["user"]["username"] == self.student_1.user.username
        assert response.data["group_id"] is None
        assert response.data["groupmate_id"] is None

    def test_student_profile_with_group_ids(self, api_client):
        api_client.force_authenticate(user=self.student_1.user)
        url = reverse("student-profile")
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data["group_id"] == self.student_group.id
        assert response.data["groupmate_id"] == self.supervisor_group.id

    def test_student_profile_unauthenticated(self, api_client):
        url = reverse("student-profile")
        response = api_client.get(url)

        assert response.status_code == 401

    def test_student_profile_user_without_student_profile(self, api_client):
        user = User.objects.create_user(
            username="other_user", password="abc123", user_type="student"
        )
        api_client.force_authenticate(user=user)
        url = reverse("student-profile")
        response = api_client.get(url)

        assert response.status_code == 404
