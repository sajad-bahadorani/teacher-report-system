from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.education.models import Classroom
from apps.models import BaseModel


class SessionReport(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    classroom = models.ForeignKey(Classroom, on_delete=models.PROTECT, related_name="session_reports")

    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="session_reports")

    session_date = models.DateTimeField()
    lesson_summary = models.TextField()

    present_count = models.PositiveIntegerField()
    absent_count = models.PositiveIntegerField()

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    submitted_at = models.DateTimeField()

    is_late = models.BooleanField(default=False)

    rejection_reason = models.TextField(null=True, blank=True)

    def calculate_is_late(self):
        if not self.submitted_at:
            return False

        deadline = self.session_date + timedelta(hours=48)

        return self.submitted_at > deadline

    def submit(self):
        self.submitted_at = timezone.now()
        self.is_late = self.calculate_is_late()
        self.status = self.Status.PENDING
        self.rejection_reason = None

    def clean(self):
        if self.status == self.Status.REJECTED and not self.rejection_reason:
            raise ValidationError({
                "rejection_reason": "Rejection reason is required."
            })

    def __str__(self):
        return (
            f"{self.teacher.full_name} - "
            f"{self.classroom} - "
            f"{self.session_date}"
        )
    

class SessionReportStatusHistory(BaseModel):
    report = models.ForeignKey(
        SessionReport,
        on_delete=models.CASCADE,
        related_name="status_history",
    )

    status = models.CharField(
        max_length=10,
        choices=SessionReport.Status.choices,
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="report_status_changes",
    )

    note = models.TextField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.report_id} - {self.status}"