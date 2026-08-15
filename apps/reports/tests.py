from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.education.models import School, Term, Classroom, TeacherAssignment
from apps.reports.models import SessionReport


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