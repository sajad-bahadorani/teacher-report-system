from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.permissions import IsTeacher, IsEducationOfficer

from .models import SessionReport
from .serializers import SessionReportSerializer, SessionReportReviewSerializer


class SessionReportListCreateView(generics.ListCreateAPIView):
    serializer_class = SessionReportSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        return SessionReport.objects.filter(
            teacher=self.request.user
        )


@extend_schema(
    parameters=[
        OpenApiParameter("school", int, OpenApiParameter.QUERY),
        OpenApiParameter("classroom", int, OpenApiParameter.QUERY),
        OpenApiParameter("teacher", int, OpenApiParameter.QUERY),
        OpenApiParameter("start_date", str, OpenApiParameter.QUERY),
        OpenApiParameter("end_date", str, OpenApiParameter.QUERY),
    ]
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
    

class SessionReportReviewView(generics.UpdateAPIView):
    queryset = SessionReport.objects.all()
    serializer_class = SessionReportReviewSerializer
    permission_classes = [IsEducationOfficer]


class SessionReportUpdateView(generics.UpdateAPIView):
    serializer_class = SessionReportSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        return SessionReport.objects.filter(
            teacher=self.request.user
        )

    def perform_update(self, serializer):
        report = self.get_object()

        if report.status != SessionReport.Status.REJECTED:
            raise ValidationError(
                "Only rejected reports can be edited."
            )

        serializer.save(
            status=SessionReport.Status.PENDING,
            rejection_reason=None,
        )
    