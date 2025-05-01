from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Student Model


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ("student", "Student"),
        ("supervisor", "Supervisor"),
        ("committee_member", "Committee Member"),
    )
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES)
    password = models.CharField(
        _("password"),
        max_length=128,
        default=(
            "pbkdf2_sha256$600000$nI24sQ6SMrCktseq"
            "8GsQEN$3g3MpxyFn93g3H7ID5xW+y7VriQhhpoCRoprZq4x4Wk="
        ),
    )

    def __str__(self):
        return self.username


class Student(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="student_profile"
    )

    registration_no = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    semester = models.CharField(max_length=100, blank=True, null=True)
    batch_no = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username


class ProjectCategories(models.Model):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name


class Supervisor(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="supervisor_profile"
    )
    supervisor_id = models.CharField(max_length=100, unique=True)
    category = models.ManyToManyField(
        ProjectCategories, related_name="supervisor", blank=True
    )

    def __str__(self):
        return self.user.username


class CommitteeMember(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="committee_member_profile"
    )
    committee_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.user.username


class Group(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("canceled", "Canceled"),
    )
    student_1 = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="send_request"
    )
    student_2 = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="receive_request"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    project_category = models.ForeignKey(
        ProjectCategories, on_delete=models.CASCADE, related_name="groupmate_project"
    )

    class Meta:
        unique_together = ("student_1", "student_2", "id")

    def __str__(self):
        return f"{self.student_1} - {self.student_2} - {self.status}"


class GroupCreationComment(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="comments")
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="comments"
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.comment}"


class Project(models.Model):
    project_category = models.ForeignKey(
        ProjectCategories, on_delete=models.CASCADE, related_name="project_category"
    )
    project_name = models.CharField(max_length=100)
    project_description = models.TextField()
    language = models.CharField(max_length=100)
    functionalities = models.TextField()

    def __str__(self):
        return f"{self.project_name} - {self.project_category}"


class NewIdeaProject(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="new_idea"
    )
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    proposal_link = models.URLField(blank=True, null=True)
    proposal_file = models.FileField(upload_to="proposals/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.student}"


class SupervisorOfStudentGroup(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted_by_student", "Accepted by Student"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("canceled", "Canceled"),
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="supervisor_request"
    )
    supervisor = models.ForeignKey(
        Supervisor, on_delete=models.CASCADE, related_name="group_request"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="supervisor_project"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="supervisor_request_created_by"
    )

    class Meta:
        unique_together = ("group", "supervisor")

    def __str__(self):
        return f"{self.group} - {self.supervisor} - {self.status}"


class SupervisorStudentComments(models.Model):
    COMMENT_BY_CHOICES = (
        ("student", "Student"),
        ("supervisor", "Supervisor"),
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_comments",
    )
    supervisor = models.ForeignKey(
        Supervisor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supervisor_comments",
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="group_comments"
    )
    comment = models.TextField()
    commented_by = models.CharField(
        max_length=20, choices=COMMENT_BY_CHOICES, default="student"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.supervisor} - {self.student} - {self.comment}"
