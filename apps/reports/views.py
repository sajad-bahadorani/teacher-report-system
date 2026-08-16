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
    serializer_class = SessionReportSerializer
    permission_classes = [IsEducationOfficer]

    def get_queryset(self):
        queryset = SessionReport.objects.all()

        school = self.request.query_params.get("school")
        classroom = self.request.query_params.get("classroom")
        teacher = self.request.query_params.get("teacher")
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if school:
            queryset = queryset.filter(
                classroom__school_id=school
            )

        if classroom:
            queryset = queryset.filter(
                classroom_id=classroom
            )

        if teacher:
            queryset = queryset.filter(
                teacher_id=teacher
            )

        if start_date:
            queryset = queryset.filter(
                session_date__date__gte=start_date
            )

        if end_date:
            queryset = queryset.filter(
                session_date__date__lte=end_date
            )

        return queryset
    