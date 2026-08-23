from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.accounts.permissions import IsFinanceOfficer
from apps.accounts.models import User

from .calculations import calculate_teacher_monthly_salary
from .models import SalaryRate, Salary
from .serializers import(
    SalaryRateSerializer,
    SalaryCalculationSerializer,
    MonthlySalaryCalculationSerializer,
)  


class SalaryRateListCreateView(generics.ListCreateAPIView):
    queryset = SalaryRate.objects.all()
    serializer_class = SalaryRateSerializer
    permission_classes = [IsFinanceOfficer]


class TeacherSalaryCalculateView(APIView):
    permission_classes = [IsFinanceOfficer]

    def post(self, request):
        serializer = SalaryCalculationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        teacher = serializer.validated_data["teacher"]
        year = serializer.validated_data["year"]
        month = serializer.validated_data["month"]

        amount = calculate_teacher_monthly_salary(teacher, year, month)

        salary, created = Salary.objects.update_or_create(
            teacher=teacher,
            year=year,
            month=month,
            defaults={
                "amount": amount,
            },
        )

        return Response({
            "teacher": teacher.id,
            "year": year,
            "month": month,
            "amount": salary.amount,
        })


class AllTeachersMonthlySalaryCalculateView(APIView):
    permission_classes = [IsFinanceOfficer]

    def post(self, request):
        serializer = MonthlySalaryCalculationSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        year = serializer.validated_data["year"]
        month = serializer.validated_data["month"]

        teachers = User.objects.filter(
            role=User.Role.TEACHER
        )

        results = []

        for teacher in teachers:
            amount = calculate_teacher_monthly_salary(
                teacher,
                year,
                month,
            )

            salary, created = Salary.objects.update_or_create(
                teacher=teacher,
                year=year,
                month=month,
                defaults={
                    "amount": amount,
                },
            )

            results.append({
                "teacher": teacher.id,
                "year": year,
                "month": month,
                "amount": salary.amount,
            })

        return Response(results)

