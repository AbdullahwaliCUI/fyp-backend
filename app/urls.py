from django.urls import path
from .views import (
    NewIdeaProjectAPIVIEW,
    GroupRequestView,
    StudentLoginView,
    StudentsListView,
    StudentProfileView,
    ChangePasswordView,
    ProjectCategoriesView,
    ProjectAPIVIEW,
    StudentProposalListAPIView,
    SupervisorStudentCommentsAPIView,
    SendSupervisorRequestAPIView,
    SupervisorResponseAPIView,
    SupervisorLoginAPIView,
    CommitteeMemberLoginAPIView,
    SupervisorprofileView,
    GroupComments,
    CommitteeMemberProfileView,
)

urlpatterns = [
    path("student/login/", StudentLoginView.as_view(), name="student-login"),
    path("student/profile/", StudentProfileView.as_view(), name="student-profile"),
    path(
        "supervisor/login/", SupervisorLoginAPIView.as_view(), name="supervisor-login"
    ),
    path(
        "supervisor/profile/",
        SupervisorprofileView.as_view(),
        name="supervisor-profile",
    ),
    path(
        "committee_member/login/",
        CommitteeMemberLoginAPIView.as_view(),
        name="committee-member-login",
    ),
    path(
        "committee_member/profile/",
        CommitteeMemberProfileView.as_view(),
        name="committee-member-profile",
    ),
    path("change_password/", ChangePasswordView.as_view(), name="change_password"),
    path("listofstudents/", StudentsListView.as_view(), name="listofstudents"),
    path(
        "project/categories/",
        ProjectCategoriesView.as_view(),
        name="project-categories",
    ),
    path("groupmate/request/", GroupRequestView.as_view(), name="groupmate-request"),
    path(
        "groupmate/<int:group>/comments/",
        GroupComments.as_view(),
        name="groupmate-comments",
    ),
    path("projects/list/", ProjectAPIVIEW.as_view(), name="projects-list"),
    path(
        "projects/new_idea/",
        NewIdeaProjectAPIVIEW.as_view(),
        name="projects-new-idea",
    ),
    path(
        "student/proposal/list/",
        StudentProposalListAPIView.as_view(),
        name="student-proposal-list",
    ),
    path(
        "supervisor/student/comments/",
        SupervisorStudentCommentsAPIView.as_view(),
        name="supervisor-student-comments",
    ),
    path(
        "supervisor/student/request/",
        SendSupervisorRequestAPIView.as_view(),
        name="supervisor-student-request",
    ),
    path(
        "supervisor/student/response/",
        SupervisorResponseAPIView.as_view(),
        name="supervisor-student-response",
    ),
]
