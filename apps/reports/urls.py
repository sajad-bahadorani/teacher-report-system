from django.urls import path

from .views import SessionReportListCreateView, EducationReportListView


urlpatterns = [
    path(
        "", SessionReportListCreateView.as_view(), name="session-report-list-create"),
        path("education/", EducationReportListView.as_view(), name="education-report-list"),
]