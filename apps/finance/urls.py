from django.urls import path

from .views import SalaryRateListCreateView, TeacherSalaryCalculateView


urlpatterns = [
    path("rates/", SalaryRateListCreateView.as_view(), name="salary-rate-list-create"),
    path("calculate/", TeacherSalaryCalculateView.as_view(), name="teacher-salary-calculate"),
]
