from rest_framework import generics

from apps.accounts.permissions import IsTeacher, IsEducationOfficer

from .models import SessionReport
from .serializers import SessionReportSerializer


class SessionReportListCreateView(generics.ListCreateAPIView):
    serializer_class = SessionReportSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        return SessionReport.objects.filter(
            teacher=self.request.user
        )

class EducationReportListView(generics.ListAPIView):
    queryset = SessionReport.objects.all()
    serializer_class = SessionReportSerializer
    permission_classes = [IsEducationOfficer]
    