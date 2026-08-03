from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

    

class User(AbstractUser):
    class Role(models.TextChoices):
        TEACHER = "teacher", "Teacher"
        EDUCATION_OFFICER = "education", "Education Officer"
        FINANCE_OFFICER = "finance", "Finance Officer"
        
    full_name = models.CharField(max_length=250)
    phone = models.CharField(max_length=11, unique=True)
    emergency_phone = models.CharField(max_length=11)
    role = models.CharField(max_length=30, choices=Role.choices)
    
    def __str__(self):
        return f"{self.full_name} - {self.role}"
    

