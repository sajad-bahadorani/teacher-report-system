from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

# Create your models here.


class User(AbstractUser):
    class Role(models.TextChoices):
        TEACHER = "teacher", "Teacher"
        EDUCATION_OFFICER = "education", "Education Officer"
        FINANCE_OFFICER = "finance", "Finance Officer"

    phone_validator = RegexValidator(regex=r"^09\d{9}$", message="Phone number must be in format 09xxxxxxxxx")   
    phone_number = models.CharField(max_length=11, unique=True, validators=[phone_validator])
    emergency_phone = models.CharField(max_length=11, validators=[phone_validator])
    role = models.CharField(max_length=30, choices=Role.choices, db_index=True)
    

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    

    def __str__(self):
        return f"{self.full_name} - {self.role}"
