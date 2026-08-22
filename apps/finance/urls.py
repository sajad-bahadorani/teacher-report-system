from django.urls import path

from .views import SalaryRateListCreateView


urlpatterns = [
    path("rates/", SalaryRateListCreateView.as_view(), name="salary-rate-list-create"),
]
