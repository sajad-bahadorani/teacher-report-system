from django.utils import timezone
from rest_framework import serializers

from apps.education.models import TeacherAssignment

from .models import SessionReport


class SessionReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionReport
        fields = "__all__"
        read_only_fields = [
            "teacher",
            "status",
            "submitted_at",
            "is_late",
            "rejection_reason",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        request = self.context["request"]
        teacher = request.user

        classroom = attrs.get("classroom", getattr(self.instance, "classroom", None))

        session_date = attrs.get("session_date", getattr(self.instance, "session_date", None))

        assignment_exists = TeacherAssignment.objects.filter(
            teacher=teacher,
            classroom=classroom,
            start_date__lte=session_date.date(),
        ).filter(
            end_date__isnull=True
        ).exists() or TeacherAssignment.objects.filter(
            teacher=teacher,
            classroom=classroom,
            start_date__lte=session_date.date(),
            end_date__gte=session_date.date(),
        ).exists()

        if not assignment_exists:
            raise serializers.ValidationError(
                 "You can only create reports for your own classroom."
            )
        return attrs

    def create(self, validated_data):
        submitted_at = timezone.now()

        report = SessionReport(
            teacher=self.context["request"].user,
            submitted_at=submitted_at,
            **validated_data,
        )

        report.is_late = report.calculate_is_late()
        report.full_clean()
        report.save()

        return report


class SessionReportReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionReport
        fields = [
            "status",
            "rejection_reason",
        ]

    def validate(self, attrs):
        status = attrs.get("status")
        rejection_reason = attrs.get("rejection_reason")

        if (
            status == SessionReport.Status.REJECTED
            and not rejection_reason
        ):
            raise serializers.ValidationError({
                "rejection_reason": "Rejection reason is required."
            })

        if status == SessionReport.Status.APPROVED:
            attrs["rejection_reason"] = None

        return attrs


class GroupApproveSerializer(serializers.Serializer):
    report_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
    )