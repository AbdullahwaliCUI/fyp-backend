# students/serializers.py
from rest_framework import serializers
from app.models import (
    Student,
    Supervisor,
    CommitteeMember,
    CustomUser,
    Group,
    GroupCreationComment,
    ProjectCategories,
    Project,
    NewIdeaProject,
    SupervisorStudentComments,
    SupervisorOfStudentGroup,
)


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "user_type"]


class StudentProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Student
        fields = ["id","user", "registration_no", "department", "semester", "batch_no"]


class SupervisorProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Supervisor
        fields = ["user", "supervisor_id"]


class CommitteeMemberProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = CommitteeMember
        fields = ["user", "committee_id"]


class ProjectCategoriesSerializer(serializers.ModelSerializer):
    supervisor = SupervisorProfileSerializer(many=True, read_only=True)

    class Meta:
        model = ProjectCategories
        fields = ["id", "category_name", "supervisor"]


class GroupStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["status"]


class GroupRequestSerializer(serializers.ModelSerializer):
    student_1 = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), write_only=True
    )
    student_2 = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), write_only=True
    )
    project_category = serializers.PrimaryKeyRelatedField(
        queryset=ProjectCategories.objects.all(), write_only=True
    )
    student_1_details = StudentProfileSerializer(read_only=True, source="student_1")
    student_2_details = StudentProfileSerializer(read_only=True, source="student_2")
    project_category_details = ProjectCategoriesSerializer(
        read_only=True, source="project_category"
    )
    # student_2 = StudentProfileSerializer(read_only=True)
    # project_category = ProjectCategoriesSerializer(read_only=True)
    # show comments of current group
    comment_count = serializers.SerializerMethodField(read_only=True)

    def get_comment_count(self, obj):
        return GroupCreationComment.objects.filter(group=obj.id).count()

    def validate(self, attrs):
        if attrs.get("student_1") == attrs.get("student_2"):
            return serializers.ValidationError("You cannot send a request to yourself.")
        return super().validate(attrs)

    def create(self, validated_data):
        obj, _ = Group.objects.get_or_create(**validated_data)
        return obj

    class Meta:
        model = Group
        fields = [
            "id",
            "student_1",
            "student_2",
            "status",
            "project_category",
            "comment_count",
            "student_1_details",
            "student_2_details",
            "project_category_details",
        ]
        read_only = ["comment_count", "status"]


# class CommentSerializer(serializers.ModelSerializer):
#     student = StudentProfileSerializer(read_only=True)

#     class Meta:
#         model = GroupCreationComment
#         fields = ["id", "comment", "group", "student", "created_at"]
#         read_only = ["id", "created_at"]


class CommentSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)

    class Meta:
        model = GroupCreationComment
        fields = ["id", "comment", "group", "student", "created_at"]
        read_only_fields = [
            "id",
            "created_at",
            "group",
            "student",
        ]  # Add 'group' and 'student'


class ProjectSerializer(serializers.ModelSerializer):
    project_category = ProjectCategoriesSerializer(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "project_category",
            "project_name",
            "project_description",
            "language",
            "functionalities",
        ]


class NewIdeaProjectSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)

    class Meta:
        model = NewIdeaProject
        fields = [
            "id",
            "student",
            "title",
            "description",
            "proposal_link",
            "proposal_file",
            "created_at",
        ]
        read_only = ["id", "created_at"]


class SupervisorStudentCommentsSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    supervisor = SupervisorProfileSerializer(read_only=True)

    class Meta:
        model = SupervisorStudentComments
        fields = ["id", "student", "supervisor", "comment", "comment_by", "created_at"]
        read_only_fields = ["id", "created_at"]


class SupervisorOfStudentGroupSerializer(serializers.ModelSerializer):
    group = GroupRequestSerializer
    supervisor = SupervisorProfileSerializer(read_only=True)

    class Meta:
        model = SupervisorOfStudentGroup
        fields = [
            "id",
            "group",
            "supervisor",
            "project",
            "status",
            "created_at",
            "created_by",
        ]
