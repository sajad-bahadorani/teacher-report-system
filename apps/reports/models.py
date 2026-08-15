from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.
class SessionReport(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        
    classroom = models.ForeignKey("education.Classroom", on_delete=models.PROTECT, related_name="session_reports")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="session_reports")
    
    session_date = models.DateField()
    
    lesson_summary = models.TextField()
    
    present_count = models.PositiveIntegerField()
    absent_count = models.PositiveIntegerField()
    
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDENUG)
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    is_late = models.BooleanField(default=False)
    
    rejection_reason = models.TextField(null=True, blank=True)
    
    def clean(self):
        if self.present_count < 0 or self.absent_count < 0:
            raise ValidationError("The number of participants cannot be negative.")
        
        if self.status == self.Status.REJECTED and not self.rejection_reson:
            raise ValidationError({"rejection_reason":"Rejection reason is required."})
        
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.classroom} - {self.session_date}"