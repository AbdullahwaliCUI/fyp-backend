import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from app.models import Student, Group, ProjectCategories, CustomUser


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def project_category():
    return ProjectCategories.objects.create(name="Test Category")


@pytest.fixture
def create_students(db):
    # Create 3 students with associated users
    users = []
    students = []
    for i in range(3):
        user = CustomUser.objects.create_user(
            username=f"user{i}", email=f"user{i}@example.com", password="password123"
        )
        users.append(user)
        student = Student.objects.create(
            user=user,
            registration_no=f"REG{i}",
            department="CS",
            semester="semester_6",
            batch_no="2024",
        )
        students.append(student)
    return students


@pytest.fixture
def logged_in_student(create_students):
    # Return the first student
    return create_students[0]


def authenticate(api_client, user):
    # Mock authentication by force_authenticate or token set, here simplified for example
    api_client.force_authenticate(user=user)


class TestStudentsListView:
    url = reverse("listofstudents")

    def test_list_students_no_filter(
        self, api_client, logged_in_student, create_students
    ):
        authenticate(api_client, logged_in_student.user)

        response = api_client.get(self.url)

        assert response.status_code == 200
        # All students should be returned with same batch_no, department, semester
        expected_ids = {student.id for student in create_students}
        returned_ids = {student["id"] for student in response.data["results"]}
        assert expected_ids == returned_ids

    def test_list_students_with_for_request_filter(
        self, api_client, logged_in_student, create_students, project_category
    ):
        # Create accepted Group relationships for filtering
        Group.objects.create(
            student_1=logged_in_student,
            student_2=create_students[1],
            status="accepted",
            project_category=project_category,
        )
        Group.objects.create(
            student_1=create_students[2],
            student_2=logged_in_student,
            status="accepted",
            project_category=project_category,
        )

        authenticate(api_client, logged_in_student.user)
        url = self.url + "?for_request=true"
        response = api_client.get(url)

        assert response.status_code == 200

        # Students with accepted group requests should be excluded
        excluded_ids = {create_students[1].id, create_students[2].id}
        returned_ids = {student["id"] for student in response.data["results"]}
        expected_ids = {student.id for student in create_students} - excluded_ids
        assert returned_ids == expected_ids

    def test_pagination_works(self, api_client, logged_in_student, create_students):
        authenticate(api_client, logged_in_student.user)

        response = api_client.get(self.url, {"page": 1, "page_size": 2})

        assert response.status_code == 200
        assert "results" in response.data
        assert len(response.data["results"]) <= 2

    def test_unauthenticated_access(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 401  # Unauthorized
