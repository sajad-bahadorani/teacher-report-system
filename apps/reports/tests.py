from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory

from apps.accounts.models import User
from apps.education.models import School, Term, Classroom, TeacherAssignment
from .models import SessionReport
from .serializers import SessionReportSerializer


class SessionReportTest(TestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher_report",
            password="1234",
            role=User.Role.TEACHER,
            phone_number="09160000001",
            emergency_phone="09160000002",
        )

        self.school = School.objects.create(
            name="Sample School"
        )

        self.term = Term.objects.create(
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=90)).date(),
            term_type=Term.TermType.NORMAL,
        )

        self.classroom = Classroom.objects.create(
            school=self.school,
            term=self.term,
            session_duration=90,
        )

        TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            start_date=self.term.start_date,
            end_date=self.term.end_date,
        )

        self.client = APIClient()

        self.education_officer = User.objects.create_user(
            username="education_report",
            password="1234",
            role=User.Role.EDUCATION_OFFICER,
            phone_number="09160000005",
            emergency_phone="09160000006",
        )

        self.finance_officer = User.objects.create_user(
            username="finance_report",
            password="1234",
            role=User.Role.FINANCE_OFFICER,
            phone_number="09160000007",
            emergency_phone="09160000008",
        )


    def test_create_session_report(self):
        session_time = timezone.now()

        report = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=session_time,
            lesson_summary="Django REST Framework",
            present_count=10,
            absent_count=2,
            submitted_at=session_time + timedelta(hours=1),
        )

        self.assertEqual(
            report.status,
            SessionReport.Status.PENDING,
        )

        self.assertEqual(
            report.present_count,
            10,
        )

        self.assertEqual(
            report.absent_count,
            2,
        )

    def test_report_is_not_late_before_48_hours(self):
        session_time = timezone.now()

        report = SessionReport(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=session_time,
            lesson_summary="Django REST Framework",
            present_count=10,
            absent_count=2,
            submitted_at=session_time + timedelta(hours=47),
        )

        self.assertFalse(report.calculate_is_late())


    def test_report_is_not_late_at_exactly_48_hours(self):
        session_time = timezone.now()

        report = SessionReport(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=session_time,
            lesson_summary="Django REST Framework",
            present_count=10,
            absent_count=2,
            submitted_at=session_time + timedelta(hours=48),
        )

        self.assertFalse(report.calculate_is_late())


    def test_report_is_late_after_48_hours(self):
        session_time = timezone.now()

        report = SessionReport(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=session_time,
            lesson_summary="Django REST Framework",
            present_count=10,
            absent_count=2,
            submitted_at=session_time + timedelta(hours=49),
        )

        self.assertTrue(report.calculate_is_late())


    def test_serializer_creates_report_for_teacher_own_classroom(self):
        factory = APIRequestFactory()

        request = factory.post("/api/reports/")
        request.user = self.teacher

        session_time = timezone.now()

        serializer = SessionReportSerializer(
            data={
                "classroom": self.classroom.id,
                "session_date": session_time,
                "lesson_summary": "Django REST Framework",
                "present_count": 10,
                "absent_count": 2,
            },
            context={
                "request": request,
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        report = serializer.save()

        self.assertEqual(
            report.teacher,
            self.teacher,
        )

        self.assertEqual(
            report.status,
            SessionReport.Status.PENDING,
        )

        self.assertIsNotNone(
            report.submitted_at,
        )

        self.assertFalse(
            report.is_late,
        )

    def test_teacher_cannot_create_report_for_another_teachers_classroom(self):
        other_teacher = User.objects.create_user(
            username="other_teacher",
            password="1234",
            role=User.Role.TEACHER,
            phone_number="09160000003",
            emergency_phone="09160000004",
        )

        factory = APIRequestFactory()
        request = factory.post("/api/reports/")
        request.user = other_teacher

        serializer = SessionReportSerializer(
            data={
                "classroom": self.classroom.id,
                "session_date": timezone.now(),
                "lesson_summary": "Django REST Framework",
                "present_count": 10,
                "absent_count": 2,
            },
            context={
                "request": request,
            },
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "non_field_errors",
            serializer.errors,
        )

    def test_teacher_cannot_create_report_outside_assignment_period(self):
        factory = APIRequestFactory()
        request = factory.post("/api/reports/")
        request.user = self.teacher

        session_time = timezone.make_aware(
            timezone.datetime(
                self.term.start_date.year,
                self.term.start_date.month,
                self.term.start_date.day,
                10,
                0,
            )
        ) - timedelta(days=1)

        serializer = SessionReportSerializer(
            data={
                "classroom": self.classroom.id,
                "session_date": session_time,
                "lesson_summary": "Django REST Framework",
                "present_count": 10,
                "absent_count": 2,
            },
            context={
                "request": request,
            },
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "non_field_errors",
            serializer.errors,
        )

    def test_teacher_can_create_report_for_own_classroom(self):
        self.client.force_authenticate(user=self.teacher)

        url = reverse("session-report-list-create")

        response = self.client.post(
            url,
            {
                "classroom": self.classroom.id,
                "session_date": timezone.now().isoformat(),
                "lesson_summary": "Introduction to Django REST Framework",
                "present_count": 10,
                "absent_count": 2,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            SessionReport.objects.count(),
            1,
        )

        report = SessionReport.objects.first()

        self.assertEqual(
            report.teacher,
            self.teacher,
        )

        self.assertEqual(
            report.status,
            SessionReport.Status.PENDING,
        )

        self.assertIsNotNone(
            report.submitted_at,
        )

    def test_education_officer_cannot_create_session_report(self):
        self.client.force_authenticate(
            user=self.education_officer
        )

        url = reverse("session-report-list-create")

        response = self.client.post(
            url,
            {
                "classroom": self.classroom.id,
                "session_date": timezone.now().isoformat(),
                "lesson_summary": "Django REST Framework",
                "present_count": 10,
                "absent_count": 2,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_finance_officer_cannot_create_session_report(self):
        self.client.force_authenticate(
            user=self.finance_officer
        )

        url = reverse("session-report-list-create")

        response = self.client.post(
            url,
            {
                "classroom": self.classroom.id,
                "session_date": timezone.now().isoformat(),
                "lesson_summary": "Django REST Framework",
                "present_count": 10,
                "absent_count": 2,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_teacher_can_list_only_own_reports(self):
        other_teacher = User.objects.create_user(
            username="other_report_teacher",
            password="1234",
            role=User.Role.TEACHER,
            phone_number="09160000009",
            emergency_phone="09160000010",
        )

        other_classroom = Classroom.objects.create(
            school=self.school,
            term=self.term,
            session_duration=60,
        )

        TeacherAssignment.objects.create(
            teacher=other_teacher,
            classroom=other_classroom,
            start_date=self.term.start_date,
            end_date=self.term.end_date,
        )

        SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="My report",
            present_count=10,
            absent_count=1,
            submitted_at=timezone.now(),
        )

        SessionReport.objects.create(
            teacher=other_teacher,
            classroom=other_classroom,
            session_date=timezone.now(),
            lesson_summary="Other teacher report",
            present_count=8,
            absent_count=2,
            submitted_at=timezone.now(),
        )

        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.get(
            reverse("session-report-list-create")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["lesson_summary"],
            "My report",
        )

    def test_education_officer_can_list_all_reports(self):
        other_teacher = User.objects.create_user(
            username="teacher_report_2",
            password="1234",
            role=User.Role.TEACHER,
            phone_number="09160000011",
            emergency_phone="09160000012",
        )

        other_classroom = Classroom.objects.create(
            school=self.school,
            term=self.term,
            session_duration=60,
        )

        TeacherAssignment.objects.create(
            teacher=other_teacher,
            classroom=other_classroom,
            start_date=self.term.start_date,
            end_date=self.term.end_date,
        )

        SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="First report",
            present_count=10,
            absent_count=1,
            submitted_at=timezone.now(),
        )

        SessionReport.objects.create(
            teacher=other_teacher,
            classroom=other_classroom,
            session_date=timezone.now(),
            lesson_summary="Second report",
            present_count=8,
            absent_count=2,
            submitted_at=timezone.now(),
        )

        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.get(
            reverse("education-report-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

    def test_teacher_cannot_access_education_report_list(self):
        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.get(
            reverse("education-report-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )