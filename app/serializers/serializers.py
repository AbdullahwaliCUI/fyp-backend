# students/serializers.py
from rest_framework import serializers
from django.db.models import Q
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
    Document,
    ScopeDocumentEvaluationCriteria,
)


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "user_type"]


class StudentProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    group_id = serializers.SerializerMethodField(read_only=True)

    def get_group_id(self, obj):
        group = SupervisorOfStudentGroup.objects.filter(
            Q(group__student_1=obj) | Q(group__student_2=obj),
            status="accepted",
        ).first()
        return group.id if group else None

    class Meta:
        model = Student
        fields = [
            "id",
            "user",
            "registration_no",
            "department",
            "semester",
            "batch_no",
            "group_id",
        ]


class SupervisorProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Supervisor
        fields = ["id", "user", "supervisor_id"]


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


class GroupCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["project_category"]


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
    comment_count = serializers.SerializerMethodField(read_only=True)

    def get_comment_count(self, obj):
        return GroupCreationComment.objects.filter(group=obj.id).count()

    def validate(self, attrs):
        if attrs.get("student_1") == attrs.get("student_2"):
            return serializers.ValidationError("You cannot send a request to yourself.")
        return super().validate(attrs)

    def create(self, validated_data):
        project_category = validated_data.pop("project_category")
        try:
            obj = Group.objects.get(**validated_data)
        except Group.DoesNotExist:
            obj = Group(**validated_data)
        obj.project_category = project_category
        obj.save()
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
        read_only_fields = ["id", "created_at"]


class ScopeDocumentEvaluationCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScopeDocumentEvaluationCriteria
        fields = "__all__"
        read_only_fields = ["id"]


class SupervisorOfStudentGroupSerializer(serializers.ModelSerializer):
    supervisor = SupervisorProfileSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    group = GroupRequestSerializer(read_only=True)

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
            "Scope_document_evaluation_form",
        ]


class SupervisorStudentModelCommentsSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    supervisor = SupervisorProfileSerializer(read_only=True)

    class Meta:
        model = SupervisorStudentComments
        fields = [
            "id",
            "group",
            "student",
            "supervisor",
            "comment",
            "commented_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by = StudentProfileSerializer(read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "uploaded_file",
            "uploaded_at",
            "status",
            "group",
            "uploaded_by",
        ]
        read_only_fields = ["uploaded_at", "status", "group", "uploaded_by"]


class DocumentStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["status"]
