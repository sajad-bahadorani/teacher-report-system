from django.db.models import Count, Q

from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.accounts.permissions import IsTeacher, IsEducationOfficer

from .models import SessionReport
from .serializers import (
    SessionReportSerializer,
    SessionReportReviewSerializer,
    GroupApproveSerializer,
)


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


class TeacherMonthlyReaportSummaryView(APIView):
    permission_classes = [IsTeacher]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="year",
                type=int,
                location=OpenApiParameter.QUERY,
                required=True,
            ),
            OpenApiParameter(
                name="month",
                type=int,
                location=OpenApiParameter.QUERY,
                required=True,
            ),
        ]
    )

    def get(self, request):
        year = request.query_params.get("year")
        month = request.query_params.get("month")

        if not year or not month:
            raise ValidationError("year and month are required.")

        reports = SessionReport.objects.filter(
            teacher=request.user,
            session_date__year=year,
            session_date__month=month,
        )

        summary = reports.aggregate(
            total=Count("id"),

            pending=Count("id", filter=Q(status=SessionReport.Status.PENDING)),

            approved=Count("id", filter=Q(status=SessionReport.Status.APPROVED)),

            rejected=Count("id", filter=Q(status=SessionReport.Status.REJECTED)),
        )

        return Response({
            "year": int(year),
            "month": int(month),
            **summary,
        })


class GroupApproveView(APIView):
    permission_classes = [IsEducationOfficer]

    def post(self, request):
        serializer = GroupApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report_ids = serializer.validated_data["report_ids"]

        reports = SessionReport.objects.filter(
            id__in=report_ids,
            status=SessionReport.Status.PENDING,
        )

        updated_count = reports.update(
            status=SessionReport.Status.APPROVED,
            rejection_reason=None,
        )

        return Response({
            "approved_count": updated_count
        })