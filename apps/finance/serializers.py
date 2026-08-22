from rest_framework import serializers

from apps.accounts.models import User

from .models import SalaryRate


class SalaryRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryRate
        fields = [
            "id",
            "teacher",
            "term",
            "base_rate",
        ]

    def validate_teacher(self, teacher):
        if teacher.role != User.Role.TEACHER:
            raise serializers.ValidationError(
                "Salary rate can only be set for teachers."
            )

        return teacher

    def validate_base_rate(self, base_rate):
        if base_rate <= 0:
            raise serializers.ValidationError(
                "Base rate must be greater than zero."
            )

        return base_rate