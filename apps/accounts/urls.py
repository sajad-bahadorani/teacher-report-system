from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import ProfileView, TeacherDashboardView, EducationDashboardView, FinanceDashboardView


urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("me/", ProfileView.as_view(), name="me"),
    path("teacher/", TeacherDashboardView.as_view(), name="teacher"),
    path("education/", EducationDashboardView.as_view(), name="education"),
    path("finance/", FinanceDashboardView.as_view(), name="finance"),
]
