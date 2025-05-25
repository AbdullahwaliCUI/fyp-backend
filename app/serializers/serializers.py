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
    SupervisorStudentComments,
    SupervisorOfStudentGroup,
    Document,
    ScopeDocumentEvaluationCriteria,
    CommitteeMemberPanel,
    CommitteeMemberTemplates,
    SRSEvaluationSupervisor,
    SRSEvaluationCommitteeMember,
    SDDEvaluationSupervisor,
    SDDEvaluationCommitteeMember,
    Evaluation3Supervisor,
    Evaluation3CommitteeMember,
    Evaluation4Supervisor,
    Evaluation4CommitteeMember,
    ChatRoom,
)


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "user_type"]


class StudentProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    group_id = serializers.SerializerMethodField(read_only=True)
    groupmate_id = serializers.SerializerMethodField(read_only=True)

    def get_group_id(self, obj):
        group = SupervisorOfStudentGroup.objects.filter(
            Q(group__student_1=obj) | Q(group__student_2=obj),
            status="accepted",
        ).first()
        return group.id if group else None

    def get_groupmate_id(self, obj):
        group = Group.objects.filter(
            Q(student_1=obj) | Q(student_2=obj),
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
            "groupmate_id",
        ]


class SupervisorProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Supervisor
        fields = [
            "id",
            "user",
            "supervisor_id",
            "research_interest",
            "academic_background",
        ]
        read_only_fields = ["id", "user", "supervisor_id"]


class CommitteeMemberProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = CommitteeMember
        fields = ["id", "user", "committee_id", "panel"]


class PanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommitteeMemberPanel
        fields = ["id", "name", "committee_member", "projects"]
        read_only_fields = ["id"]


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
    groups_data = serializers.SerializerMethodField(read_only=True)

    def get_groups_data(self, obj):
        return obj.groups.filter(status="accepted").values_list(flat=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "project_category",
            "project_name",
            "project_description",
            "language",
            "functionalities",
            "groups_data",
        ]

        read_only_fields = ["id", "groups_data"]

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data.update({"user": request.user})
        response = super().create(validated_data=validated_data)
        Project.objects.filter(user=request.user).exclude(pk=response.pk).delete()
        return response


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
            "srs_evaluation_supervisor",
            "srs_evaluation_committee_member",
            "sdd_evaluation_supervisor",
            "sdd_evaluation_committee_member",
            "evaluation3_supervisor",
            "evaluation3_committee_member",
            "evaluation4_supervisor",
            "evaluation4_committee_member",
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
    document_type = serializers.CharField(required=False)

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "document_type",
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


class CommitteeMemberTemplatesSerializer(serializers.ModelSerializer):
    uploaded_by = CommitteeMemberProfileSerializer(read_only=True)
    template_type = serializers.CharField(required=False)

    class Meta:
        model = CommitteeMemberTemplates
        fields = [
            "id",
            "title",
            "uploaded_by",
            "uploaded_file",
            "uploaded_at",
            "semester",
            "template_type",
        ]


class SRSEvaluationSupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SRSEvaluationSupervisor
        fields = [
            "id",
            "regularity",
            "srs_are_frs_mapped_to_the_problem",
            "srs_are_nfr_mapped_to_the_problem",
            "is_srs_storyboarding",
            "according_to_requirement",
            "is_srs_template_followed",
            "is_write_up_correct",
            "student_participation",
            "comment",
            "total_marks",
        ]
        read_only_fields = ["id"]


class SRSEvaluationCommitteeMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = SRSEvaluationCommitteeMember
        fields = [
            "id",
            "analysis_of_existing_systems",
            "problem_defined",
            "proposed_solution",
            "tools_technologies",
            "frs_mapped",
            "nfrs_mapped",
            "requirements_analysis",
            "mocks_defined",
            "srs_template_followed",
            "technical_writeup_correct",
            "domain_knowledge",
            "qa_ability",
            "presentation_attire",
            "comment",
            "total_marks",
        ]
        read_only_fields = ["id"]


class SDDEvaluationSupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SDDEvaluationSupervisor
        fields = [
            "id",
            "data_representation_diagram",
            "process_flow",
            "design_models",
            "algorithms_defined",
            "module_completion_status",
            "is_sdd_template_followed",
            "is_technical_writeup_correct",
            "regularity",
            "seminar_participation",
            "comment",
            "total_marks",
        ]
        read_only_fields = ["id"]


class SDDEvaluationCommitteeMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = SDDEvaluationCommitteeMember
        fields = [
            "id",
            "data_representation_diagram",
            "process_flow",
            "sdd_design_models",
            "algorithm_defined",
            "modules_completion_status",
            "sdd_template_followed",
            "techincal_writeup_correct",
            "project_domain_knowledge",
            "qa_ability",
            "proper_attire",
            "comment",
            "total_marks",
        ]
        read_only_fields = ["id"]


class Evaluation3SupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation3Supervisor
        fields = [
            "id",
            "module_completion",
            "software_testing",
            "regularity",
            "project_domain_knowledge",
            "is_template_followed",
            "is_writeup_correct",
            "comment",
            "total_marks",
        ]
        read_only_fields = ["id"]


class Evaluation3CommitteeMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation3CommitteeMember
        fields = [
            "id",
            "module_completion",
            "software_testing",
            "qa_ability",
            "proper_attire",
            "is_template_followed",
            "is_writeup_correct",
            "comment",
            "total_marks",
        ]
        read_only_fields = ["id"]


class Evaluation4SupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation4Supervisor
        fields = [
            "id",
            "module_completion",
            "student_participation_seminar",
            "is_template_followed",
            "is_writeup_correct",
            "comment",
            "total_marks",
        ]
        read_only_fields = ["id"]


class Evaluation4CommitteeMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation4CommitteeMember
        fields = [
            "id",
            "module_completion",
            "software_testing",
            "qa_ability",
            "proper_attire",
            "is_template_followed",
            "is_writeup_correct",
            "comment",
            "total_marks",
        ]
        read_only_fields = ["id"]


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "group",
            "student",
            "supervisor",
            "message",
            "sent_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
