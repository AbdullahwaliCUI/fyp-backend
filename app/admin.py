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
admin.site.register(SupervisorStudentComments)
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


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["project_name", "project_category", "panel", "user"]

    list_filter = ["project_category__category_name", "panel"]
    readonly_fields = ("user",)  

    fieldsets = (
        ("Project Information", {
            "fields": ("project_name", "project_description", "project_category")
        }),
        ("Technical Details", {
            "fields": ("language", "functionalities")
        }),
        ("Assignment", {
            "fields": ("panel", "user")
        }),
    )


@admin.register(SupervisorOfStudentGroup)
class SupervisorOfStudentGroupAdmin(admin.ModelAdmin):
    list_display = ["supervisor", "group", "status", "project"]

    list_filter = ["status", "project__panel"]
