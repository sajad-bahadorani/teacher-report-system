from django.urls import path

from .views import SessionReportListCreateView, EducationReportListView, SessionReportReviewView


urlpatterns = [
    path("", SessionReportListCreateView.as_view(), name="session-report-list-create"),
    path("education/", EducationReportListView.as_view(), name="education-report-list"),
    path("<int:pk>/review/", SessionReportReviewView.as_view(), name="session-report-review"),
]