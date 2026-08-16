from django.urls import path

from .views import SessionReportListCreateView


urlpatterns = [
    path(
        "", SessionReportListCreateView.as_view(), name="session-report-list-create"),
]