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
    end_date = models.DateField(null=True, blank=True)
    term_type = models.CharField(max_length=10, choices=TermType.choices)
    
    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError({"end": "Term end date cannot be before start date."})
        
    def __str__(self):
        return f"{self.start} - {self.end}"
    
    

class Classroom(models.Model):
    class Duration(models.IntegerChoices):
        MINUTES_60 = 60, "60 minutes"
        MINUTES_90 = 90, "90 minutes"
        MINUTES_120 = 120, "120 minutes"
        
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
            raise ValidationError({"end_date": "End date cannot be before start date."})
        
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.classroom}"