from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Student Model


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ("student", "Student"),
        ("supervisor", "Supervisor"),
        ("committee_member", "Committee Member"),
    )
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES)
    password = models.CharField(
        _("password"),
        max_length=128,
        default=(
            "pbkdf2_sha256$600000$nI24sQ6SMrCktseq"
            "8GsQEN$3g3MpxyFn93g3H7ID5xW+y7VriQhhpoCRoprZq4x4Wk="
        ),
    )

    def __str__(self):
        return self.username


class Student(models.Model):
    SEMESTER_CHOICES = (
        ("semester_6", "Semester 6"),
        ("semester_7", "Semester 7"),
        ("semester_8", "Semester 8"),
    )
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="student_profile"
    )

    registration_no = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    semester = models.CharField(
        max_length=100, choices=SEMESTER_CHOICES, blank=True, null=True
    )
    batch_no = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username


class ProjectCategories(models.Model):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name


class Supervisor(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="supervisor_profile"
    )
    supervisor_id = models.CharField(max_length=100, unique=True)
    research_interest = models.CharField(max_length=255, blank=True, null=True)
    academic_background = models.CharField(
        max_length=255, blank=True, null=True
    )
    
    category = models.ManyToManyField(
        ProjectCategories, related_name="supervisor", blank=True
    )

    def __str__(self):
        return self.user.username


class Group(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("canceled", "Canceled"),
    )
    student_1 = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="send_request"
    )
    student_2 = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="receive_request"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    project_category = models.ForeignKey(
        ProjectCategories, on_delete=models.CASCADE, related_name="groupmate_project"
    )

    class Meta:
        unique_together = ("student_1", "student_2", "id")

    def __str__(self):
        return f"{self.student_1} - {self.student_2} - {self.status}"


class GroupCreationComment(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="comments")
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="comments"
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.comment}"


class CommitteeMemberPanel(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name if self.name else "Committee Member Panel"


class Project(models.Model):
    project_category = models.ForeignKey(
        ProjectCategories, on_delete=models.CASCADE, related_name="project_category"
    )
    panel = models.ForeignKey(
        CommitteeMemberPanel, on_delete=models.CASCADE, related_name="projects"
    )
    project_name = models.CharField(max_length=100)
    project_description = models.TextField()
    language = models.CharField(max_length=100)
    functionalities = models.TextField()

    def __str__(self):
        return f"{self.project_name} - {self.project_category}"


class NewIdeaProject(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="new_idea"
    )
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    proposal_link = models.URLField(blank=True, null=True)
    proposal_file = models.FileField(upload_to="proposals/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.student}"


class ScopeDocumentEvaluationCriteria(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("marginal", "Marginal"),
        ("adequate", "Adequate"),
        ("good", "Good"),
        ("excellent", "Excellent"),
    )
    problem_statement = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default="pending"
    )
    validity_of_he_proposed_solution = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default="pending"
    )
    motivation_behind_tools_and_technologies = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default="pending"
    )
    modules = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default="pending"
    )
    task_management = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default="pending"
    )
    related_system_analysis = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default="pending"
    )
    document_format = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default="pending"
    )
    plagiarism_report = models.BooleanField(null=True, blank=True)
    comments = models.TextField(blank=True, null=True)
    evaluation_status = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return f"scope_document_{self.id}"


class SRSEvaluationSupervisor(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("marginal", "Marginal"),
        ("adequate", "Adequate"),
        ("good", "Good"),
        ("excellent", "Excellent"),
    )
    regularity = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    srs_are_frs_mapped_to_the_problem = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    srs_are_nfr_mapped_to_the_problem = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    is_srs_storyboarding = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    according_to_requirement = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    is_srs_template_followed = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    is_write_up_correct = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    student_participation = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    comment = models.CharField(max_length=255, null=True, blank=True)

    @staticmethod
    def percentages_dict() -> dict:
        return {
            "pending": 0,
            "marginal": 15,
            "adequate": 40,
            "good": 70,
            "excellent": 95,
        }

    @classmethod
    def calculate(cls, key, marks) -> float:
        return (cls.percentages_dict().get(key, 0) / 100) * marks

    @property
    def total_marks(self) -> float:
        return (
            self.calculate(self.regularity, 5)
            + self.calculate(self.srs_are_frs_mapped_to_the_problem, 4)
            + self.calculate(self.srs_are_nfr_mapped_to_the_problem, 1)
            + self.calculate(self.is_srs_storyboarding, 3)
            + self.calculate(self.according_to_requirement, 2)
            + self.calculate(self.is_srs_template_followed, 2)
            + self.calculate(self.is_write_up_correct, 3)
            + self.calculate(self.student_participation, 5)
        )

    def __str__(self):
        return f"srs_{self.id}"


class SRSEvaluationCommitteeMember(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("marginal", "Marginal"),
        ("adequate", "Adequate"),
        ("good", "Good"),
        ("excellent", "Excellent"),
    )
    analysis_of_existing_systems = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    problem_defined = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    proposed_solution = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    tools_technologies = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    frs_mapped = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    nfrs_mapped = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    requirements_analysis = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    mocks_defined = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    srs_template_followed = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    technical_writeup_correct = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    domain_knowledge = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    qa_ability = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    presentation_attire = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    comment = models.CharField(max_length=255, null=True, blank=True)

    @staticmethod
    def percentages_dict():
        return {
            "pending": 0,
            "marginal": 0.15,
            "adequate": 0.40,
            "good": 0.70,
            "excellent": 0.95,
        }

    @classmethod
    def calculate(cls, key, max_marks):
        return cls.percentages_dict().get(key, 0) * max_marks

    @property
    def total_marks(self):
        return (
            self.calculate(self.analysis_of_existing_systems, 0.5)
            + self.calculate(self.problem_defined, 2.5)
            + self.calculate(self.proposed_solution, 1.5)
            + self.calculate(self.tools_technologies, 0.5)
            + self.calculate(self.frs_mapped, 4)
            + self.calculate(self.nfrs_mapped, 2)
            + self.calculate(self.requirements_analysis, 3)
            + self.calculate(self.mocks_defined, 2)
            + self.calculate(self.srs_template_followed, 2)
            + self.calculate(self.technical_writeup_correct, 3)
            + self.calculate(self.domain_knowledge, 1)
            + self.calculate(self.qa_ability, 2)
            + self.calculate(self.presentation_attire, 1)
        )

    def __str__(self):
        return f"srs_{self.id}"


class SDDEvaluationSupervisor(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("marginal", "Marginal"),
        ("adequate", "Adequate"),
        ("good", "Good"),
        ("excellent", "Excellent"),
    )
    data_representation_diagram = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    process_flow = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    design_models = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    algorithms_defined = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    module_completion_status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    is_sdd_template_followed = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    is_technical_writeup_correct = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    regularity = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    seminar_participation = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    comment = models.CharField(max_length=255, null=True, blank=True)

    @staticmethod
    def percentages_dict() -> dict:
        return {
            "pending": 0,
            "marginal": 15,
            "adequate": 40,
            "good": 70,
            "excellent": 95,
        }

    @classmethod
    def calculate(cls, key, marks) -> float:
        return (cls.percentages_dict().get(key, 0) / 100) * marks

    @property
    def total_marks(self) -> float:
        return (
            self.calculate(self.data_representation_diagram, 2)
            + self.calculate(self.process_flow, 2)
            + self.calculate(self.design_models, 4)
            + self.calculate(self.algorithms_defined, 2)
            + self.calculate(self.module_completion_status, 5)
            + self.calculate(self.is_sdd_template_followed, 2)
            + self.calculate(self.is_technical_writeup_correct, 3)
            + self.calculate(self.regularity, 2.5)
            + self.calculate(self.seminar_participation, 2.5)
        )

    def __str__(self):
        return f"sdd_{self.id}"


class SDDEvaluationCommitteeMember(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("marginal", "Marginal"),
        ("adequate", "Adequate"),
        ("good", "Good"),
        ("excellent", "Excellent"),
    )
    data_representation_diagram = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    process_flow = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    sdd_design_models = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    algorithm_defined = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    modules_completion_status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    sdd_template_followed = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    techincal_writeup_correct = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    project_domain_knowledge = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    qa_ability = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    proper_attire = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    comment = models.CharField(max_length=255, null=True, blank=True)

    @staticmethod
    def percentages_dict() -> dict:
        return {
            "pending": 0,
            "marginal": 15,
            "adequate": 40,
            "good": 70,
            "excellent": 95,
        }

    @classmethod
    def calculate(cls, key, marks) -> float:
        return (cls.percentages_dict().get(key, 0) / 100) * marks

    @property
    def total_marks(self) -> float:
        return (
            self.calculate(self.data_representation_diagram, 2)
            + self.calculate(self.process_flow, 2)
            + self.calculate(self.sdd_design_models, 5)
            + self.calculate(self.algorithm_defined, 2)
            + self.calculate(self.modules_completion_status, 5)
            + self.calculate(self.sdd_template_followed, 2)
            + self.calculate(self.techincal_writeup_correct, 3)
            + self.calculate(self.project_domain_knowledge, 1)
            + self.calculate(self.qa_ability, 2)
            + self.calculate(self.proper_attire, 1)
        )

    def __str__(self):
        return f"sdd_{self.id}"


class Evaluation3Supervisor(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("marginal", "Marginal"),
        ("adequate", "Adequate"),
        ("good", "Good"),
        ("excellent", "Excellent"),
    )
    module_completion = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    software_testing = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    regularity = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    is_template_followed = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    project_domain_knowledge = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    is_writeup_correct = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )

    comment = models.CharField(max_length=255, null=True, blank=True)

    @staticmethod
    def percentages_dict():
        return {
            "marginal": 15,
            "adequate": 40,
            "good": 70,
            "excellent": 95,
        }

    @classmethod
    def calculate(cls, key, marks):
        return (cls.percentages_dict().get(key, 0) / 100) * marks

    @property
    def total_marks(self):
        return (
            self.calculate(self.module_completion, 3)
            + self.calculate(self.software_testing, 4)
            + self.calculate(self.regularity, 3)
            + self.calculate(self.is_template_followed, 2)
            + self.calculate(self.project_domain_knowledge, 2.5)
            + self.calculate(self.is_writeup_correct, 3)
        )

    def __str__(self):
        return f"supervisor_eval_{self.id}"


class Evaluation3CommitteeMember(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("marginal", "Marginal"),
        ("adequate", "Adequate"),
        ("good", "Good"),
        ("excellent", "Excellent"),
    )
    module_completion = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    software_testing = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    qa_ability = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    proper_attire = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    is_template_followed = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    is_writeup_correct = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )

    comment = models.CharField(max_length=255, null=True, blank=True)

    @staticmethod
    def percentages_dict():
        return {
            "marginal": 15,
            "adequate": 40,
            "good": 70,
            "excellent": 95,
        }

    @classmethod
    def calculate(cls, key, marks):
        return (cls.percentages_dict().get(key, 0) / 100) * marks

    @property
    def total_marks(self):
        return (
            self.calculate(self.module_completion, 4)
            + self.calculate(self.software_testing, 4)
            + self.calculate(self.qa_ability, 2.5)
            + self.calculate(self.proper_attire, 0.5)
            + self.calculate(self.is_template_followed, 1)
            + self.calculate(self.is_writeup_correct, 3)
        )

    def __str__(self):
        return f"committee_member_eval_{self.id}"


class Evaluation4Supervisor(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("marginal", "Marginal"),
        ("adequate", "Adequate"),
        ("good", "Good"),
        ("excellent", "Excellent"),
    )
    module_completion = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    student_participation_seminar = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    is_template_followed = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    is_writeup_correct = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )

    comment = models.CharField(max_length=255, null=True, blank=True)

    @staticmethod
    def percentages_dict():
        return {
            "marginal": 15,
            "adequate": 40,
            "good": 70,
            "excellent": 95,
        }

    @classmethod
    def calculate(cls, key, marks):
        return (cls.percentages_dict().get(key, 0) / 100) * marks

    @property
    def total_marks(self):
        return (
            self.calculate(self.module_completion, 5)
            + self.calculate(self.student_participation_seminar, 5)
            + self.calculate(self.is_template_followed, 2)
            + self.calculate(self.is_writeup_correct, 3)
        )

    def __str__(self):
        return f"supervisor_eval_{self.id}"


class Evaluation4CommitteeMember(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("marginal", "Marginal"),
        ("adequate", "Adequate"),
        ("good", "Good"),
        ("excellent", "Excellent"),
    )
    module_completion = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    software_testing = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    qa_ability = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    proper_attire = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    is_template_followed = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    is_writeup_correct = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending"
    )

    comment = models.CharField(max_length=255, null=True, blank=True)

    @staticmethod
    def percentages_dict():
        return {
            "marginal": 15,
            "adequate": 40,
            "good": 70,
            "excellent": 95,
        }

    @classmethod
    def calculate(cls, key, marks):
        return (cls.percentages_dict().get(key, 0) / 100) * marks

    @property
    def total_marks(self):
        return (
            self.calculate(self.module_completion, 4)
            + self.calculate(self.software_testing, 4)
            + self.calculate(self.qa_ability, 2.5)
            + self.calculate(self.proper_attire, 0.5)
            + self.calculate(self.is_template_followed, 1)
            + self.calculate(self.is_writeup_correct, 3)
        )

    def __str__(self):
        return f"committee_member_eval_{self.id}"


class SupervisorOfStudentGroup(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted_by_student", "Accepted by Student"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("canceled", "Canceled"),
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="supervisor_request"
    )
    supervisor = models.ForeignKey(
        Supervisor, on_delete=models.CASCADE, related_name="group_request"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="groups"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="supervisor_request_created_by"
    )
    Scope_document_evaluation_form = models.OneToOneField(
        ScopeDocumentEvaluationCriteria,
        on_delete=models.CASCADE,
        related_name="scope_document_evaluation_form",
        blank=True,
        null=True,
    )
    srs_evaluation_supervisor = models.OneToOneField(
        SRSEvaluationSupervisor,
        on_delete=models.CASCADE,
        related_name="supervisor_of_students",
        blank=True,
        null=True,
    )
    srs_evaluation_committee_member = models.OneToOneField(
        SRSEvaluationCommitteeMember,
        on_delete=models.CASCADE,
        related_name="supervisor_of_students",
        blank=True,
        null=True,
    )
    sdd_evaluation_supervisor = models.OneToOneField(
        SDDEvaluationSupervisor,
        on_delete=models.CASCADE,
        related_name="supervisor_of_students",
        blank=True,
        null=True,
    )
    sdd_evaluation_committee_member = models.OneToOneField(
        SDDEvaluationCommitteeMember,
        on_delete=models.CASCADE,
        related_name="supervisor_of_students",
        blank=True,
        null=True,
    )
    evaluation3_supervisor = models.OneToOneField(
        Evaluation3Supervisor,
        on_delete=models.CASCADE,
        related_name="supervisor_of_students",
        blank=True,
        null=True,
    )
    evaluation3_committee_member = models.OneToOneField(
        Evaluation3CommitteeMember,
        on_delete=models.CASCADE,
        related_name="supervisor_of_students",
        blank=True,
        null=True,
    )
    evaluation4_supervisor = models.OneToOneField(
        Evaluation4Supervisor,
        on_delete=models.CASCADE,
        related_name="supervisor_of_students",
        blank=True,
        null=True,
    )
    evaluation4_committee_member = models.OneToOneField(
        Evaluation4CommitteeMember,
        on_delete=models.CASCADE,
        related_name="supervisor_of_students",
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs):
        if not self.Scope_document_evaluation_form:
            self.Scope_document_evaluation_form = (
                ScopeDocumentEvaluationCriteria.objects.create()
            )
        if not self.srs_evaluation_supervisor:
            self.srs_evaluation_supervisor = SRSEvaluationSupervisor.objects.create()
        if not self.srs_evaluation_committee_member:
            self.srs_evaluation_committee_member = (
                SRSEvaluationCommitteeMember.objects.create()
            )
        if not self.sdd_evaluation_supervisor:
            self.sdd_evaluation_supervisor = SDDEvaluationSupervisor.objects.create()
        if not self.sdd_evaluation_committee_member:
            self.sdd_evaluation_committee_member = (
                SDDEvaluationCommitteeMember.objects.create()
            )
        if not self.evaluation3_supervisor:
            self.evaluation3_supervisor = Evaluation3Supervisor.objects.create()
        if not self.evaluation3_committee_member:
            self.evaluation3_committee_member = (
                Evaluation3CommitteeMember.objects.create()
            )
        if not self.evaluation4_supervisor:
            self.evaluation4_supervisor = Evaluation4Supervisor.objects.create()
        if not self.evaluation4_committee_member:
            self.evaluation4_committee_member = (
                Evaluation4CommitteeMember.objects.create()
            )
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("group", "supervisor")

    def __str__(self):
        return f"{self.group} - {self.supervisor} - {self.status}"


class SupervisorStudentComments(models.Model):
    COMMENT_BY_CHOICES = (
        ("student", "Student"),
        ("supervisor", "Supervisor"),
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_comments",
    )
    supervisor = models.ForeignKey(
        Supervisor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supervisor_comments",
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="group_comments"
    )
    comment = models.TextField()
    commented_by = models.CharField(
        max_length=20, choices=COMMENT_BY_CHOICES, default="student"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.supervisor} - {self.student} - {self.comment}"


class CommitteeMember(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="committee_member_profile"
    )
    committee_id = models.CharField(max_length=100, unique=True)
    panel = models.ForeignKey(
        CommitteeMemberPanel, on_delete=models.CASCADE, related_name="committee_member"
    )

    def __str__(self):
        return self.user.username


class Document(models.Model):
    DOCUMENT_TYPE_CHOICES = (
        ("scope_document", "Scope Document"),
        ("srs_document", "SRS Document"),
        ("sdd_document", "SDD Document"),
        ("final_report_document", "Final Report Document")
    )
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted_by_student", "Accepted by Student"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("canceled", "Canceled"),
    )
    group = models.ForeignKey(
        SupervisorOfStudentGroup, on_delete=models.CASCADE, related_name="documents"
    )
    uploaded_by = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="uploaded_documents"
    )
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    title = models.CharField(max_length=100)
    uploaded_file = models.FileField(upload_to="documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


class CommitteeMemberTemplates(models.Model):
    TEMPLATE_TYPE_CHOICES = (
        ("srs_template", "SRS Template"),
        ("sdd_template", "SDD Template"),
        ("final_report_template", "Final Report Template"),
    )
    SEMESTER_CHOICES = (
        ("semester_6", "Semester 6"),
        ("semester_7", "Semester 7"),
        ("semester_8", "Semester 8"),
    )
    semester = models.CharField(max_length=100, choices=SEMESTER_CHOICES)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPE_CHOICES)
    uploaded_by = models.ForeignKey(
        CommitteeMember,
        on_delete=models.CASCADE,
        related_name="uploaded_templates",
        blank=True,
        null=True,
    )
    title = models.CharField(max_length=100)
    uploaded_file = models.FileField(upload_to="templates/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


class ChatRoom(models.Model):
    MESSAGE_BY_CHOICES = (
        ("student", "Student"),
        ("supervisor", "Supervisor"),
    )
    group = models.ForeignKey(
        SupervisorOfStudentGroup, on_delete=models.CASCADE, related_name="chat_messages"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_messages",
    )
    supervisor = models.ForeignKey(
        Supervisor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supervisor_messages",
    )
    message = models.TextField()
    sent_by = models.CharField(max_length=20, choices=MESSAGE_BY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sent_by}: {self.message[:30]}"
