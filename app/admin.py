# students/admin.py
from typing import Any

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
from project_lib.admin import ImportableExportableAdmin, Workbook, RecordImportError

admin.site.register(CustomUser)
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
        (
            "Project Information",
            {"fields": ("project_name", "project_description", "project_category")},
        ),
        ("Technical Details", {"fields": ("language", "functionalities")}),
        ("Assignment", {"fields": ("panel", "user")}),
    )


@admin.register(SupervisorOfStudentGroup)
class SupervisorOfStudentGroupAdmin(admin.ModelAdmin):
    list_display = ["supervisor", "group", "status", "project"]

    list_filter = ["status", "project__panel"]


@admin.register(Student)
class StudentAdmin(ImportableExportableAdmin):
    list_display = ["user", "registration_no", "department", "semester", "batch_no"]

    change_list_template = "admin/import_changelist.html"

    def import_parse_and_save_xlsx_data(
        self, extra_params: dict[str, Any], workbook: Workbook
    ) -> tuple[int, int]:
        worksheet = workbook.active

        columns = [
            cell_value
            for row in worksheet.iter_rows(
                max_row=1, max_col=worksheet.max_column, values_only=True
            )
            for cell_value in row
            if cell_value
        ]

        errors: dict[int | str, str | list[int]] = {}
        records_created = 0

        for row_idx, row in enumerate(
            worksheet.iter_rows(
                min_row=2,
                max_row=worksheet.max_row,
                max_col=len(columns) + 1,
                values_only=True,
            )
        ):
            if not row or all(v is None for v in row):
                break

            record_field_values = {}

            try:
                for col_idx, current_column in enumerate(columns):
                    if current_column not in self.import_related_fields:
                        record_field_values[current_column] = row[col_idx]

                try:
                    Student.objects.create(
                        registration_no=record_field_values.get("registration_no", ""),
                        department=record_field_values.get("department", ""),
                        semester=record_field_values.get("semester", "").lower(),
                        batch_no=record_field_values.get("batch_no", ""),
                        user=CustomUser.objects.create(
                            username=record_field_values.get("username", ""),
                            email=record_field_values.get("email", ""),
                            user_type="student",
                        ),
                    )
                    records_created += 1

                except Exception as e:
                    errors[row_idx] = f"Error creating user/student: {str(e)}"

            except Exception as e:
                errors[row_idx] = f"Error processing row data: {str(e)}"

            except (ValueError, Exception) as ex:
                msg = str(ex)
                if msg not in errors:
                    errors[msg] = []
                errors[msg].append(row_idx + 2)  # type: ignore[union-attr]
        records_updated = 0
        if errors:
            raise RecordImportError(errors)
        else:
            return records_created, records_updated
