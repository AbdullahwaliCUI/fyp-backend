# students/admin.py
from django.contrib import admin
from .models import (
    Student,
    Supervisor,
    CommitteeMember,
    CustomUser,
    ProjectCategories,
    Group,
    GroupCreationComment,
    Project,
    SupervisorStudentComments,
    SupervisorOfStudentGroup,
    CommitteeMemberPanel,
    ScopeDocumentEvaluationCriteria,
    SRSEvaluationSupervisor,
    SRSEvaluationCommitteeMember,
    SDDEvaluationCommitteeMember,
    SDDEvaluationSupervisor,
    Evaluation3Supervisor,
    Evaluation3CommitteeMember,
    Evaluation4CommitteeMember,
    Evaluation4Supervisor,
    ChatRoom,
)


admin.site.register(CustomUser)
admin.site.register(Student)
admin.site.register(Supervisor)
admin.site.register(CommitteeMember)
admin.site.register(ProjectCategories)
admin.site.register(Group)
admin.site.register(GroupCreationComment)
admin.site.register(Project)
admin.site.register(SupervisorStudentComments)
admin.site.register(SupervisorOfStudentGroup)
admin.site.register(CommitteeMemberPanel)
admin.site.register(ScopeDocumentEvaluationCriteria)
admin.site.register(SRSEvaluationSupervisor)
admin.site.register(SRSEvaluationCommitteeMember)
admin.site.register(SDDEvaluationSupervisor)
admin.site.register(SDDEvaluationCommitteeMember)
admin.site.register(Evaluation3Supervisor)
admin.site.register(Evaluation3CommitteeMember)
admin.site.register(Evaluation4Supervisor)
admin.site.register(Evaluation4CommitteeMember)
admin.site.register(ChatRoom)
