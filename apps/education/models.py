from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


# Create your models here.
class School(models.Model):
    name = models.CharField(max_length=150)
    
    def __str__(self):
        return self.name
    
    
    
class Term(models.Model):
    class TermType(models.TextChoices):
        NORMAL = "normal", "Normal"
        SUMMER = "summer", "Summer"
        
    start_date = models.DateField()
    end_date = models.DateField()
    term_type = models.CharField(max_length=10, choices=TermType.choices)
    
    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({
                "end_date": "Term end date cannot be before start date."
            })
        
    def __str__(self):
        return f"{self.start_date} - {self.end_date}"
    
    

class Classroom(models.Model):
    class Duration(models.IntegerChoices):
        MINUTES_60 = 60, "60 minutes"
        MINUTES_90 = 90, "90 minutes"
        MINUTES_120 = 120, "120 minutes"

    name = models.CharField(max_length=100)
        
    school = models.ForeignKey(School, on_delete=models.PROTECT, related_name="classrooms")
    term = models.ForeignKey(Term, on_delete=models.PROTECT, related_name="classrooms")
    
    session_duration = models.PositiveSmallIntegerField(choices=Duration.choices)
    
    def __str__(self):
        return f"{self.school.name} - {self.term} - {self.session_duration} min"
    
    
    
class TeacherAssignment(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="teacher_assignments")
    classroom = models.ForeignKey(Classroom, on_delete=models.PROTECT, related_name="teacher_assignments")
    
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({
                "end_date": "End date cannot be before start date."
            })

        if self.teacher_id and self.teacher.role != self.teacher.Role.TEACHER:
            raise ValidationError({
                "teacher": "Only teachers can be assigned to a classroom."
            })

        if self.classroom_id:
            term = self.classroom.term

            if self.start_date < term.start_date:
                raise ValidationError({
                    "start_date": "Assignment cannot start before the term starts."
                })

            if self.end_date and term.end_date and self.end_date > term.end_date:
                raise ValidationError({
                    "end_date": "Assignment cannot end after the term ends."
                })

        if self.classroom_id and self.start_date:
            overlapping_assignments = TeacherAssignment.objects.filter(
                classroom=self.classroom,
                start_date__lte=(
                    self.end_date
                    if self.end_date
                    else self.classroom.term.end_date
                ),
            ).filter(
                models.Q(end_date__isnull=True)
                | models.Q(end_date__gte=self.start_date)
            )

            if self.pk:
                overlapping_assignments = overlapping_assignments.exclude(
                    pk=self.pk
                )

            if overlapping_assignments.exists():
                raise ValidationError({
                    "start_date": (
                        "This classroom already has a teacher "
                        "assigned during this period."
                    )
                })