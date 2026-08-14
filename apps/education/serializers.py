from django.db import models

from rest_framework import serializers

from .models import Classroom, School, Term, TeacherAssignment


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = "__all__"


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = "__all__"

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({
                "end_date": "End date cannot be before start date."
            })

        return attrs


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = "__all__"


class TeacherAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherAssignment
        fields = "__all__"

    def validate_teacher(self, value):
        if value.role != value.Role.TEACHER:
            raise serializers.ValidationError(
                "Only teachers can be assigned to a classroom."
            )

        return value

    def validate(self, attrs):
        start_date = attrs.get(
            "start_date",
            self.instance.start_date if self.instance else None
        )

        end_date = attrs.get(
            "end_date",
            self.instance.end_date if self.instance else None
        )

        classroom = attrs.get(
            "classroom",
            self.instance.classroom if self.instance else None
        )

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({
                "end_date": "End date cannot be before start date."
            })

        if classroom and start_date:
            term = classroom.term

            if start_date < term.start_date:
                raise serializers.ValidationError({
                    "start_date": "Assignment cannot start before the term starts."
                })

            if end_date and end_date > term.end_date:
                raise serializers.ValidationError({
                    "end_date": "Assignment cannot end after the term ends."
                })

            overlapping_assignments = TeacherAssignment.objects.filter(
                classroom=classroom,
                start_date__lte=(
                    end_date if end_date else term.end_date
                ),
            ).filter(
                models.Q(end_date__isnull=True)
                | models.Q(end_date__gte=start_date)
            )

            if self.instance:
                overlapping_assignments = overlapping_assignments.exclude(
                    pk=self.instance.pk
                )

            if overlapping_assignments.exists():
                raise serializers.ValidationError({
                    "start_date": (
                        "This classroom already has a teacher "
                        "assigned during this period."
                    )
                })

        return attrs