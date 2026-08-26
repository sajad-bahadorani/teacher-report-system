from django.conf import settings
from django.db import models
from django.db.models import Q

# Create your models here.
class SalaryRate(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="salary_rates")
    term = models.ForeignKey("education.Term", on_delete=models.PROTECT, related_name="salary_rates")
    
    base_rate = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["teacher", "term"], name="unique_teacher_term_salary_rate"),
            models.CheckConstraint(condition=Q(base_rate__gt=0), name="salary_rate_greater_than_zero"),
        ]
        
    def __str__(self):
        return f"{self.teacher.full_name} - {self.term} - {self.base_rate}"
    
    
class Salary(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="salaries")
    
    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()
    
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["teacher", "month", "year"], name="unique_teacher_month_salary"),
            models.CheckConstraint(condition=Q(month__gte=1) & Q(month__lte=12), name="salary_month_between_1_and_12"),
            models.CheckConstraint(condition=Q(amount__gte=0), name="salary_amount_not_negative"),
        ]
        
    def __str__(self):
        return f"{self.teacher.full_name} - {self.year}/{self.month} - {self.amount}"
