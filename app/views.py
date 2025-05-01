from .paginators import BasePagination
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    UpdateAPIView,
)
from django.db.models import Q
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework import status
from .models import (
    Student,
    Supervisor,
    CommitteeMember,
    GroupCreationComment,
    SupervisorStudentComments,
    ProjectCategories,
    Group,
    Project,
    NewIdeaProject,
    SupervisorOfStudentGroup,
)
from app.serializers.serializers import (
    SupervisorStudentModelCommentsSerializer,
    CommentSerializer,
    ProjectCategoriesSerializer,
    GroupRequestSerializer,
    StudentProfileSerializer,
    GroupStatusSerializer,
    ProjectSerializer,
    NewIdeaProjectSerializer,
    SupervisorOfStudentGroupSerializer,
    SupervisorProfileSerializer,
    CommitteeMemberProfileSerializer,
    GroupCategorySerializer,
)
from .serializers.field_serializers import (
    ChangePasswordDetailSerializer,
    StudentLoginDetailSerializer,
    SupervisorLoginDetailSerializer,
    CommitteeMemberLoginDetailSerializer,
    SupervisorofStudentGroupSerializer,
    SupervisorStudentCommentsSerializer,
)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh["user_type"] = user.user_type

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "expire_time": datetime.now()
        + settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME")
        - timedelta(hours=1),
    }


class ChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = ChangePasswordDetailSerializer(data=request.data)
        if serializer.is_valid():
            if not user.check_password(serializer.validated_data.get("old_password")):
                return Response(
                    {"message": "Old password is incorrect"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.set_password(serializer.validated_data.get("new_password"))
            user.save()
            return Response(
                {"message": "Password changed successfully"}, status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentLoginView(APIView):
    def post(self, request):
        serializer = StudentLoginDetailSerializer(data=request.data)
        if serializer.is_valid():
            student = Student.objects.filter(
                registration_no=serializer.validated_data.get("registration_no")
            ).first()
            if student and student.user.check_password(
                serializer.validated_data.get("password")
            ):
                token = get_tokens_for_user(student.user)
                return Response(token, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid credentials"}, status=401)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class StudentProfileView(RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = StudentProfileSerializer
    queryset = Student.objects.all()

    def get_object(self):
        return self.get_queryset().get(user=self.request.user)


class StudentsListView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = StudentProfileSerializer
    queryset = Student.objects.all()
    pagination_class = BasePagination

    def get_queryset(self):
        student = Student.objects.get(user=self.request.user)
        queryset = (
            super()
            .get_queryset()
            .filter(
                batch_no=student.batch_no,
                department=student.department,
                semester=student.semester,
            )
        )
        return queryset


class ProjectCategoriesView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectCategoriesSerializer
    queryset = ProjectCategories.objects.all()
    pagination_class = BasePagination


class GroupRequestView(CreateAPIView, UpdateAPIView, ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = GroupRequestSerializer
    queryset = Group.objects.all()

    def get_queryset(self):
        requested = self.request.GET.get("requested")
        if requested == "to":  # student sended from that student to other student
            return super().get_queryset().filter(student_1__user=self.request.user)
        elif requested == "from":  # student received from other student to that student
            return super().get_queryset().filter(student_2__user=self.request.user)
        return super().get_queryset()

    def post(self, request, *args, **kwargs):
        try:
            student_1 = Student.objects.get(user=request.user)
            serializer = GroupRequestSerializer(
                data={
                    **request.data,
                    "student_1": student_1.id,
                }
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Student.DoesNotExist:
            return Response(
                {"message": "Student not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, *args, **kwargs):
        try:
            grouo_id = request.GET.get("pk")
            group = Group.objects.get(id=grouo_id)
            if group.student_1.user == request.user:
                serializer = GroupCategorySerializer(
                    instance=group, data=request.data, partial=True
                )
            else:
                serializer = GroupStatusSerializer(
                    instance=group, data=request.data, partial=True
                )
            if serializer.is_valid():
                serializer.save()
                if serializer.data.get("status"):
                    Group.objects.filter(
                        ~Q(id=group.id),
                        Q(student_1__user=request.user)
                        | Q(student_2__user=request.user)
                        | Q(student_1=group.student_1)
                        | Q(student_2=group.student_1),
                        status="pending",
                    ).update(status="canceled")
                return Response(serializer.data, status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except Group.DoesNotExist:
            return Response(
                {"message": "Group mate request not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GroupComments(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "group"
    lookup_field = "group"

    def post(self, request, group):
        try:
            # Get the student and group instances
            student = Student.objects.get(user=request.user)
            group_instance = Group.objects.get(id=group)
        except Student.DoesNotExist:
            return Response(
                {"message": "Student not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Group.DoesNotExist:
            return Response(
                {"message": "Group not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Initialize serializer with request data
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            # Save with the student and group instances
            serializer.save(student=student, group=group_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, group):
        try:
            group_comments = GroupCreationComment.objects.filter(group=group)
            serializer = CommentSerializer(group_comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except GroupCreationComment.DoesNotExist:
            return Response({"message": "No comments found"}, status=404)


class ProjectAPIVIEW(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        category_id = self.request.GET.get("category_id")
        if category_id:
            return Project.objects.filter(project_category_id=category_id)
        return Project.objects.all()


class NewIdeaProjectAPIVIEW(CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            student = Student.objects.get(user=request.user)
            serializer = NewIdeaProjectSerializer(
                {**request.data, "student": student.id}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Student.DoesNotExist:
            return Response(
                {"message": "Student not found"}, status=status.HTTP_404_NOT_FOUND
            )


class StudentProposalListAPIView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = NewIdeaProject

    def get_queryset(self):
        student = Student.objects.get(user=self.request.user)
        return NewIdeaProject.objects.filter(student=student)


class ListSuperisorAPIView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = SupervisorProfileSerializer
    queryset = Supervisor.objects.all()
    pagination_class = BasePagination

    def get_queryset(self):
        category = self.request.GET.get("category")
        if category:
            return super().get_queryset().filter(category__id=category)
        return super().get_queryset()


class SendSupervisorRequestAPIView(CreateAPIView, ListAPIView, UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = SupervisorOfStudentGroupSerializer
    queryset = SupervisorOfStudentGroup.objects.all()
    pagination_class = BasePagination

    def get_queryset(self):
        requested = self.request.GET.get("requested")
        try:
            student = Student.objects.get(user=self.request.user)
            group = Group.objects.get(
                Q(student_1=student) | Q(student_2=student), status="accepted"
            )
            query_set = super().get_queryset().filter(group=group.id)
            if requested == "to":
                return query_set.filter(created_by__user=self.request.user)
            elif requested == "from":
                return query_set.exclude(created_by__user=self.request.user)
            else:
                return query_set
        except Group.DoesNotExist:
            pass
        except Student.DoesNotExist:
            pass
        try:
            return (
                super()
                .get_queryset()
                .filter(
                    supervisor__user=self.request.user,
                    status__in=["accepted", "accepted_by_student"],
                )
            )
        except Supervisor.DoesNotExist:
            pass
        return super().get_queryset()

    def post(self, request):
        serializer = SupervisorofStudentGroupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        try:
            student = Student.objects.get(user=request.user)
            group = Group.objects.get(
                Q(student_1=student) | Q(student_2=student), status="accepted"
            )
            supervisor = Supervisor.objects.get(
                id=serializer.validated_data["supervisor"]
            )
            project = Project.objects.get(id=serializer.validated_data["project"])
            if SupervisorOfStudentGroup.objects.filter(
                group=group.id, supervisor=supervisor
            ).exists():
                return Response(
                    {"message": "Supervisor already assigned to this group"}, status=400
                )
            supervisor_request = SupervisorOfStudentGroup.objects.create(
                group=group, supervisor=supervisor, project=project, created_by=student
            )
            serializer = SupervisorOfStudentGroupSerializer(supervisor_request)
            return Response(serializer.data, status=201)
        except Group.DoesNotExist:
            return Response({"message": "Group mate not found"}, status=404)
        except Supervisor.DoesNotExist:
            return Response({"message": "Supervisor not found"}, status=404)

    def update(self, request, *args, **kwargs):
        try:
            id = self.request.GET.get("pk")
            try:
                student = Student.objects.get(user=self.request.user)
            except Supervisor.DoesNotExist:
                student
            if student:
                if not id:
                    return Response(
                        {"message": "Supervisor request id not found"}, status=400
                    )
                group = Group.objects.get(
                    Q(student_1__user=self.request.user)
                    | Q(student_2__user=self.request.user),
                    status="accepted",
                )
                if not group:
                    return Response({"message": "Group mate not found"}, status=404)
                if group.student_1.user == self.request.user:
                    response_student = group.student_2
                elif group.student_2.user == self.request.user:
                    response_student = group.student_1
                else:
                    return Response(
                        {"message": "You are not a member of this group"}, status=404
                    )
            supervisor_request = SupervisorOfStudentGroup.objects.get(id=id)
            if student:
                if supervisor_request.created_by.user == self.request.user:
                    return Response(
                        {"message": "You cannot update this request"}, status=400
                    )
                if supervisor_request.created_by != response_student:
                    return Response(
                        {"message": "You cannot update this request"}, status=400
                    )
            serializer = SupervisorOfStudentGroupSerializer(
                instance=supervisor_request, data=request.data, partial=True
            )
            if serializer.is_valid():
                if student:
                    if serializer.validated_data.get("status") != "accepted_by_student":
                        return Response(
                            {"message": "Invalid status"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except SupervisorOfStudentGroup.DoesNotExist:
            return Response(
                {"message": "Supervisor request not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class SupervisorStudentCommentsAPIView(CreateAPIView, ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = SupervisorStudentModelCommentsSerializer
    queryset = SupervisorStudentComments.objects.all()

    def get_queryset(self):
        student = Student.objects.get(user=self.request.user)
        if student:
            group_id = self.request.GET.get("group")
            if group_id:
                return super().get_queryset().filter(group=group_id)
            return super().get_queryset()
        return super().get_queryset()

    def post(self, request):
        serializer = SupervisorStudentCommentsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        commented_by = None
        try:
            group = Group.objects.get(id=serializer.validated_data["group"])
        except Group.DoesNotExist:
            return Response({"message": "Group not found"}, status=404)
        try:
            student = Student.objects.get(user=request.user)
            commented_by = "student"
        except Student.DoesNotExist:
            student = None
        try:
            supervisor = Supervisor.objects.get(user=request.user)
            commented_by = "supervisor"
        except Supervisor.DoesNotExist:
            supervisor = None
        if not student and not supervisor:
            return Response(
                {"message": "You are not a member of this group"}, status=404
            )
        student_supervisor_comment = SupervisorStudentComments(
            comment=serializer.validated_data["comment"],
            commented_by=commented_by,
            group=group,
            student=student,
            supervisor=supervisor,
        )
        student_supervisor_comment.save()
        return Response(
            {"message": "Comment added successfully"}, status=status.HTTP_201_CREATED
        )


class SupervisorResponseAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        supervisor_studet_id = request.data.get("supervisor_student_id")
        status = request.data.get("status")

        try:
            supervisor_request = SupervisorOfStudentGroup.objects.get(
                id=supervisor_studet_id
            )
            if status == "accepted":
                supervisor_request.status = "accepted"
            elif status == "rejected":
                supervisor_request.status = "rejected"
            else:
                return Response({"message": "Invalid status"}, status=400)

            supervisor_request.save()
            serializer = SupervisorOfStudentGroupSerializer(supervisor_request)
            return Response(serializer.data, status=200)
        except SupervisorOfStudentGroup.DoesNotExist:
            return Response({"message": "Supervisor request not found"}, status=404)


class SupervisorLoginAPIView(APIView):
    def post(self, request):
        serializer = SupervisorLoginDetailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            supervisor = Supervisor.objects.filter(user__email=email).first()
            if supervisor and supervisor.user.check_password(
                serializer.validated_data.get("password")
            ):
                token = get_tokens_for_user(supervisor.user)
                return Response(token, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid credentials"}, status=401)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class SupervisorprofileView(RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = SupervisorProfileSerializer
    queryset = Supervisor.objects.all()

    def get_object(self):
        return self.get_queryset().get(user=self.request.user)


class CommitteeMemberLoginAPIView(APIView):
    def post(self, request):
        serializer = CommitteeMemberLoginDetailSerializer(request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            committeeMember = CommitteeMember.objects.filter(user__email=email).first()
            if committeeMember and committeeMember.user.check_password(
                serializer.validated_data.get("password")
            ):
                token = get_tokens_for_user(committeeMember.user)
                return Response(token, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid credentials"}, status=401)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class CommitteeMemberProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CommitteeMemberProfileSerializer
    queryset = CommitteeMember.objects.all()

    def get_object(self):
        return self.get_queryset().get(user=self.request.user)
