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
admin.site.register(Group)
admin.site.register(GroupCreationComment)
admin.site.register(SupervisorStudentComments)
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

        errors: dict[int | str, list] = {}
        records_created = 0
        records_updated = 0

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
                    try:
                        student = Student.objects.get(
                            registration_no=record_field_values.get("registration_no")
                        )
                        student.department = record_field_values.get(
                            "department", student.department
                        )
                        student.semester = record_field_values.get(
                            "semester", student.semester
                        ).lower()
                        student.batch_no = record_field_values.get(
                            "batch_no", student.batch_no
                        )
                        student.user.username = record_field_values.get(
                            "username", student.user.username
                        )
                        student.user.email = record_field_values.get(
                            "email", student.user.email
                        )
                        student.user.save()
                        student.save()
                        records_updated += 1
                    except Student.DoesNotExist:
                        username = record_field_values.get("username", "")
                        if not username:
                            errors[f"username required, skipping record: {row_idx}"] = [
                                row_idx
                            ]
                            continue
                        try:
                            CustomUser.objects.get(username=username)
                            errors[
                                f"username ({username}) already taken, skipping record: {row_idx}"
                            ] = [row_idx]
                        except CustomUser.DoesNotExist:
                            Student.objects.create(
                                registration_no=record_field_values.get(
                                    "registration_no", ""
                                ),
                                department=record_field_values.get("department", ""),
                                semester=record_field_values.get(
                                    "semester", ""
                                ).lower(),
                                batch_no=record_field_values.get("batch_no", ""),
                                user=CustomUser.objects.create(
                                    username=record_field_values.get("username", ""),
                                    email=record_field_values.get("email", ""),
                                    user_type="student",
                                ),
                            )
                            records_created += 1

                except Exception as e:
                    errors[f"Error creating user/student: {str(e)}"] = [row_idx]

            except Exception as e:
                errors[f"Error processing row data: {str(e)}"] = [row_idx]

            except (ValueError, Exception) as ex:
                msg = str(ex)
                if msg not in errors:
                    errors[msg] = []
                errors[msg].append(row_idx + 2)  # type: ignore[union-attr]
        if errors:
            raise RecordImportError(errors)
        else:
            return records_created, records_updated


@admin.register(Supervisor)
class SupervisorAdmin(ImportableExportableAdmin):
    list_display = ["user", "supervisor_id", "research_interest", "academic_background"]

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

        errors: dict[int | str, list] = {}
        records_created = 0
        records_updated = 0

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
                    try:
                        supervisor = Supervisor.objects.get(
                            supervisor_id=record_field_values.get("supervisor_id")
                        )
                        supervisor.research_interest = record_field_values.get(
                            "research_interest", supervisor.research_interest
                        )
                        supervisor.academic_background = record_field_values.get(
                            "academic_background", supervisor.academic_background
                        )
                        supervisor.user.username = record_field_values.get(
                            "username", supervisor.user.username
                        )
                        supervisor.user.email = record_field_values.get(
                            "email", supervisor.user.email
                        )
                        supervisor.user.save()
                        supervisor.save()
                        records_updated += 1
                    except Supervisor.DoesNotExist:
                        supervisor = Supervisor.objects.create(
                            supervisor_id=record_field_values.get("supervisor_id"),
                            research_interest=record_field_values.get(
                                "research_interest", ""
                            ),
                            academic_background=record_field_values.get(
                                "academic_background", ""
                            ).lower(),
                            user=CustomUser.objects.create(
                                username=record_field_values.get("username", ""),
                                email=record_field_values.get("email", ""),
                                user_type="supervisor",
                            ),
                        )
                        supervisor.save()
                        records_created += 1

                    categories = record_field_values.get("categories", "").split(",")
                    for category in categories:
                        category, _ = ProjectCategories.objects.get_or_create(
                            category_name=category.strip()
                        )
                        supervisor.category.add(category)

                except Exception as e:
                    errors[row_idx] = [
                        f"Error creating user/supervisor: {str(e)}",
                    ]

            except Exception as e:
                errors[row_idx] = [
                    f"Error processing row data: {str(e)}",
                ]

            except (ValueError, Exception) as ex:
                msg = str(ex)
                if msg not in errors:
                    errors[msg] = []
                errors[msg].append(row_idx + 2)  # type: ignore[union-attr]
        if errors:
            raise RecordImportError(errors)
        else:
            return records_created, records_updated


@admin.register(CommitteeMember)
class CommitteeMemberAdmin(ImportableExportableAdmin):
    list_display = ["user", "committee_id", "panel"]

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

        errors: dict[int | str, list] = {}
        records_created = 0
        records_updated = 0

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
                    try:
                        committee = CommitteeMember.objects.get(
                            committee_id=record_field_values.get("committee_id")
                        )
                        committee.panel.name = record_field_values.get(
                            "panel_name", committee.panel.name
                        )
                        committee.user.username = record_field_values.get(
                            "username", committee.user.username
                        )
                        committee.user.email = record_field_values.get(
                            "email", committee.user.email
                        )
                        committee.user.save()
                        committee.save()
                        records_updated += 1
                    except Supervisor.DoesNotExist:
                        panel, _ = CommitteeMemberPanel.objects.get_or_create(
                            name=record_field_values.get("panel_name")
                        )
                        committee = CommitteeMember.objects.create(
                            committee_id=record_field_values.get("committee_id"),
                            user=CustomUser.objects.create(
                                username=record_field_values.get("username", ""),
                                email=record_field_values.get("email", ""),
                                user_type="supervisor",
                            ),
                            panel=panel,
                        )
                        committee.save()
                        records_created += 1

                except Exception as e:
                    errors[row_idx] = [
                        f"Error creating user/Committee Member: {str(e)}",
                    ]

            except Exception as e:
                errors[row_idx] = [
                    f"Error processing row data: {str(e)}",
                ]

            except (ValueError, Exception) as ex:
                msg = str(ex)
                if msg not in errors:
                    errors[msg] = []
                errors[msg].append(row_idx + 2)  # type: ignore[union-attr]
        if errors:
            raise RecordImportError(errors)
        else:
            return records_created, records_updated


@admin.register(ProjectCategories)
class ProjectCategoriesAdmin(ImportableExportableAdmin):
    list_display = [
        "category_name",
    ]

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

        errors: dict[int | str, list] = {}
        records_created = 0
        records_updated = 0

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
                    _, created = ProjectCategories.objects.get_or_create(
                        category_name=record_field_values.get("category_name")
                    )
                    if created:
                        records_created += 1
                    else:
                        records_updated += 1

                except Exception as e:
                    errors[row_idx] = [
                        f"Error creating user/Committee Member: {str(e)}",
                    ]

            except Exception as e:
                errors[row_idx] = [
                    f"Error processing row data: {str(e)}",
                ]

            except (ValueError, Exception) as ex:
                msg = str(ex)
                if msg not in errors:
                    errors[msg] = []
                errors[msg].append(row_idx + 2)  # type: ignore[union-attr]
        if errors:
            raise RecordImportError(errors)
        else:
            return records_created, records_updated


@admin.register(CommitteeMemberPanel)
class CommitteeMemberPanelAdmin(ImportableExportableAdmin):
    list_display = [
        "name",
    ]

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

        errors: dict[int | str, list] = {}
        records_created = 0
        records_updated = 0

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
                    _, created = CommitteeMemberPanel.objects.get_or_create(
                        name=record_field_values.get("name")
                    )
                    if created:
                        records_created += 1
                    else:
                        records_updated += 1

                except Exception as e:
                    errors[row_idx] = [
                        f"Error creating user/Committee Member: {str(e)}",
                    ]

            except Exception as e:
                errors[row_idx] = [
                    f"Error processing row data: {str(e)}",
                ]

            except (ValueError, Exception) as ex:
                msg = str(ex)
                if msg not in errors:
                    errors[msg] = []
                errors[msg].append(row_idx + 2)  # type: ignore[union-attr]
        if errors:
            raise RecordImportError(errors)
        else:
            return records_created, records_updated
