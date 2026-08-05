from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

    

class User(AbstractUser):
    class Role(models.TextChoices):
        TEACHER = "teacher", "Teacher"
        EDUCATION_OFFICER = "education", "Education Officer"
        FINANCE_OFFICER = "finance", "Finance Officer"
        
    phone_number = models.CharField(max_length=11, unique=True)
    emergency_phone = models.CharField(max_length=11)
    role = models.CharField(max_length=30, choices=Role.choices)
    

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    

    def __str__(self):
        return f"{self.full_name} - {self.role}"
