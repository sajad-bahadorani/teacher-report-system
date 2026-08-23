from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.education.models import Term, School, Classroom
from apps.reports.models import SessionReport

from .calculations import calculate_teacher_monthly_salary
from .models import SalaryRate, Salary


class SalaryRateAPITest(APITestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="salary_teacher",
            password="1234",
            role=User.Role.TEACHER,
            phone_number="09161111111",
            emergency_phone="09162222222",
        )

        self.finance_officer = User.objects.create_user(
            username="salary_finance",
            password="1234",
            role=User.Role.FINANCE_OFFICER,
            phone_number="09163333333",
            emergency_phone="09164444444",
        )

        self.education_officer = User.objects.create_user(
            username="salary_education",
            password="1234",
            role=User.Role.EDUCATION_OFFICER,
            phone_number="09165555555",
            emergency_phone="09166666666",
        )

        self.term = Term.objects.create(
            start_date=date(2026, 8, 1),
            end_date=date(2026, 10, 30),
            term_type=Term.TermType.NORMAL,
        )

        self.url = reverse("salary-rate-list-create")


    def test_finance_officer_can_create_salary_rate(self):
        self.client.force_authenticate(
            user=self.finance_officer
        )

        response = self.client.post(
            self.url,
            {
                "teacher": self.teacher.id,
                "term": self.term.id,
                "base_rate": "200000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            SalaryRate.objects.filter(
                teacher=self.teacher,
                term=self.term,
                base_rate=Decimal("200000.00"),
            ).exists()
        )

    def test_teacher_cannot_create_salary_rate(self):
        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.post(
            self.url,
            {
                "teacher": self.teacher.id,
                "term": self.term.id,
                "base_rate": "200000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_education_officer_cannot_create_salary_rate(self):
        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.post(
            self.url,
            {
                "teacher": self.teacher.id,
                "term": self.term.id,
                "base_rate": "200000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_salary_rate_must_be_unique_per_teacher_and_term(self):
        SalaryRate.objects.create(
            teacher=self.teacher,
            term=self.term,
            base_rate=Decimal("200000.00"),
        )

        self.client.force_authenticate(
            user=self.finance_officer
        )

        response = self.client.post(
            self.url,
            {
                "teacher": self.teacher.id,
                "term": self.term.id,
                "base_rate": "250000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            SalaryRate.objects.filter(
                teacher=self.teacher,
                term=self.term,
            ).count(),
            1,
        )

    def test_salary_rate_can_only_be_set_for_teacher(self):
        self.client.force_authenticate(
            user=self.finance_officer
        )

        response = self.client.post(
            self.url,
            {
                "teacher": self.education_officer.id,
                "term": self.term.id,
                "base_rate": "200000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_base_rate_must_be_greater_than_zero(self):
        self.client.force_authenticate(
            user=self.finance_officer
        )

        response = self.client.post(
            self.url,
            {
                "teacher": self.teacher.id,
                "term": self.term.id,
                "base_rate": "0",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


class SalaryCalculationTest(TestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="salary_calc_teacher",
            password="1234",
            role=User.Role.TEACHER,
            phone_number="09167777777",
            emergency_phone="09168888888",
        )

        self.school = School.objects.create(
            name="Salary Test School"
        )

        self.term = Term.objects.create(
            start_date=date(2026, 8, 1),
            end_date=date(2026, 10, 30),
            term_type=Term.TermType.NORMAL,
        )

        self.classroom_90 = Classroom.objects.create(
            name="Class 90",
            school=self.school,
            term=self.term,
            session_duration=90,
        )

        self.classroom_60 = Classroom.objects.create(
            name="Class 60",
            school=self.school,
            term=self.term,
            session_duration=60,
        )

        self.classroom_120 = Classroom.objects.create(
            name="Class 120",
            school=self.school,
            term=self.term,
            session_duration=120,
        )

        SalaryRate.objects.create(
            teacher=self.teacher,
            term=self.term,
            base_rate=Decimal("200000.00"),
        )

    def test_salary_calculation_matches_document_example(self):
        base_session_time = timezone.make_aware(
            timezone.datetime(2026, 8, 1, 10, 0)
        )

        for i in range(10):
            session_time = base_session_time + timedelta(days=i)

            SessionReport.objects.create(
                teacher=self.teacher,
                classroom=self.classroom_90,
                session_date=session_time,
                lesson_summary=f"90 minute session {i}",
                present_count=10,
                absent_count=2,
                submitted_at=session_time + timedelta(hours=1),
                status=SessionReport.Status.APPROVED,
                is_late=False,
            )

        for i in range(2):
            session_time = base_session_time + timedelta(days=10 + i)

            SessionReport.objects.create(
                teacher=self.teacher,
                classroom=self.classroom_60,
                session_date=session_time,
                lesson_summary=f"60 minute session {i}",
                present_count=10,
                absent_count=2,
                submitted_at=session_time + timedelta(hours=1),
                status=SessionReport.Status.APPROVED,
                is_late=False,
            )

        session_time = base_session_time + timedelta(days=12)

        SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom_120,
            session_date=session_time,
            lesson_summary="120 minute session",
            present_count=10,
            absent_count=2,
            submitted_at=session_time + timedelta(hours=1),
            status=SessionReport.Status.APPROVED,
            is_late=False,
        )

        late_session_time = base_session_time + timedelta(days=13)

        SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom_90,
            session_date=late_session_time,
            lesson_summary="Late approved session",
            present_count=10,
            absent_count=2,
            submitted_at=late_session_time + timedelta(hours=49),
            status=SessionReport.Status.APPROVED,
            is_late=True,
        )

        wage = calculate_teacher_monthly_salary(
            self.teacher,
            2026,
            8,
        )

        self.assertEqual(
            wage,
            Decimal("2540000.00"),
        )

    def test_salary_is_zero_when_teacher_has_no_approved_reports(self):
        wage = calculate_teacher_monthly_salary(
            self.teacher,
            2026,
            8,
        )

        self.assertEqual(
            wage,
            Decimal("0.00"),
        )

    def test_summer_term_salary_has_ten_percent_bonus(self):
        summer_term = Term.objects.create(
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 31),
            term_type=Term.TermType.SUMMER,
        )

        summer_classroom = Classroom.objects.create(
            name="Summer Class",
            school=self.school,
            term=summer_term,
            session_duration=90,
        )

        SalaryRate.objects.create(
            teacher=self.teacher,
            term=summer_term,
            base_rate=Decimal("200000.00"),
        )

        session_time = timezone.make_aware(
            timezone.datetime(2026, 8, 10, 10, 0)
        )

        SessionReport.objects.create(
            teacher=self.teacher,
            classroom=summer_classroom,
            session_date=session_time,
            lesson_summary="Summer session",
            present_count=10,
            absent_count=2,
            submitted_at=session_time + timedelta(hours=1),
            status=SessionReport.Status.APPROVED,
            is_late=False,
        )

        wage = calculate_teacher_monthly_salary(
            self.teacher,
            2026,
            8,
        )

        self.assertEqual(
            wage,
            Decimal("220000.00"),
        )

class TeacherSalaryCalculateAPITest(APITestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="salary_api_teacher",
            password="1234",
            role=User.Role.TEACHER,
            phone_number="09170000001",
            emergency_phone="09170000002",
        )

        self.finance_officer = User.objects.create_user(
            username="salary_api_finance",
            password="1234",
            role=User.Role.FINANCE_OFFICER,
            phone_number="09170000003",
            emergency_phone="09170000004",
        )

        self.education_officer = User.objects.create_user(
            username="salary_api_education",
            password="1234",
            role=User.Role.EDUCATION_OFFICER,
            phone_number="09170000005",
            emergency_phone="09170000006",
        )

        self.school = School.objects.create(
            name="Salary API School"
        )

        self.term = Term.objects.create(
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 31),
            term_type=Term.TermType.NORMAL,
        )

        self.classroom = Classroom.objects.create(
            name="Salary API Class",
            school=self.school,
            term=self.term,
            session_duration=90,
        )

        SalaryRate.objects.create(
            teacher=self.teacher,
            term=self.term,
            base_rate=Decimal("200000.00"),
        )

        session_time = timezone.make_aware(
            timezone.datetime(2026, 8, 10, 10, 0)
        )

        SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=session_time,
            lesson_summary="Salary API report",
            present_count=10,
            absent_count=2,
            submitted_at=session_time + timedelta(hours=1),
            status=SessionReport.Status.APPROVED,
            is_late=False,
        )

        self.url = reverse("teacher-salary-calculate")

    def test_finance_officer_can_calculate_teacher_salary(self):
        self.client.force_authenticate(
            user=self.finance_officer
        )

        response = self.client.post(
            self.url,
            {
                "teacher": self.teacher.id,
                "year": 2026,
                "month": 8,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            Decimal(str(response.data["amount"])),
            Decimal("200000.00"),
        )

        self.assertTrue(
            Salary.objects.filter(
                teacher=self.teacher,
                year=2026,
                month=8,
                amount=Decimal("200000.00"),
            ).exists()
        )

    def test_teacher_cannot_calculate_salary(self):
        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.post(
            self.url,
            {
                "teacher": self.teacher.id,
                "year": 2026,
                "month": 8,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_education_officer_cannot_calculate_salary(self):
        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.post(
            self.url,
            {
                "teacher": self.teacher.id,
                "year": 2026,
                "month": 8,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_salary_calculation_rejects_invalid_month(self):
        self.client.force_authenticate(
            user=self.finance_officer
        )

        response = self.client.post(
            self.url,
            {
                "teacher": self.teacher.id,
                "year": 2026,
                "month": 13,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )