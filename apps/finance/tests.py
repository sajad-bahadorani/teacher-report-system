from datetime import date
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.education.models import Term

from .models import SalaryRate


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