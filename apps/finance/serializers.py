from rest_framework import serializers

from apps.accounts.models import User

from .models import SalaryRate, Salary


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


class SalaryCalculationSerializer(serializers.Serializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role=User.Role.TEACHER))
    year = serializers.IntegerField(min_value=1)
    month = serializers.IntegerField(min_value=1, max_value=12)
    

class MonthlySalaryCalculationSerializer(serializers.Serializer):
    year = serializers.IntegerField(min_value=1)
    month = serializers.IntegerField(
        min_value=1,
        max_value=12,
    )
