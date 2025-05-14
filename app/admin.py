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
    NewIdeaProject,
    SupervisorStudentComments,
    SupervisorOfStudentGroup,
    CommitteeMemberPanel,
    ScopeDocumentEvaluationCriteria,
    SRSEvaluation,
)


admin.site.register(CustomUser)
admin.site.register(Student)
admin.site.register(Supervisor)
admin.site.register(CommitteeMember)
admin.site.register(ProjectCategories)
admin.site.register(Group)
admin.site.register(GroupCreationComment)
admin.site.register(Project)
admin.site.register(NewIdeaProject)
admin.site.register(SupervisorStudentComments)
admin.site.register(SupervisorOfStudentGroup)
admin.site.register(CommitteeMemberPanel)
admin.site.register(ScopeDocumentEvaluationCriteria)
admin.site.register(SRSEvaluation)
