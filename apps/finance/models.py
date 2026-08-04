from django.conf import settings
from django.db import models

# Create your models here.
class SalaryRate(models.model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="salary_rates")
    term = models.ForeignKey("education.Term", on_delete=models.PROTECT, related_name="salary_rates")
    
    base_rate = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        constraints = models.UniqueConstraint(fields=["teacher", "term"], name="unique_teacher_term_salary_rate")
        
    def __str__(self):
        return f"{self.teacher.full_name} - {self.term} - {self.base_rate}"
    
    
class Salary(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="salary")
    
    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()
    
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    
    class Meta:
        constraints = models.UniqueConstraint(fields=["teacher", "month", "year"], name="unique_teacher_month_salary")
        
    def __str__(self):
        return f"{self.teacher.full_name} - {self.year}/{self.month} - {self.amount}"
