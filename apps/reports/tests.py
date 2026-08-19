from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.education.models import School, Term, Classroom, TeacherAssignment
from .models import SessionReport, SessionReportStatusHistory
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

    def test_education_officer_can_filter_reports_by_teacher(self):
        other_teacher = User.objects.create_user(
            username="filter_teacher",
            password="1234",
            role=User.Role.TEACHER,
            phone_number="09160000013",
            emergency_phone="09160000014",
        )

        other_classroom = Classroom.objects.create(
            school=self.school,
            term=self.term,
            session_duration=60,
        )

        SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Teacher one report",
            present_count=10,
            absent_count=1,
            submitted_at=timezone.now(),
        )

        SessionReport.objects.create(
            teacher=other_teacher,
            classroom=other_classroom,
            session_date=timezone.now(),
            lesson_summary="Teacher two report",
            present_count=8,
            absent_count=2,
            submitted_at=timezone.now(),
        )

        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.get(
            reverse("education-report-list"),
            {"teacher": self.teacher.id},
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
            "Teacher one report",
        )

    def test_education_officer_can_filter_reports_by_school_and_classroom(self):
        other_school = School.objects.create(
            name="Other School"
        )

        other_classroom = Classroom.objects.create(
            school=other_school,
            term=self.term,
            session_duration=60,
        )

        SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Main classroom report",
            present_count=10,
            absent_count=1,
            submitted_at=timezone.now(),
        )

        SessionReport.objects.create(
            teacher=self.teacher,
            classroom=other_classroom,
            session_date=timezone.now(),
            lesson_summary="Other classroom report",
            present_count=8,
            absent_count=2,
            submitted_at=timezone.now(),
        )

        self.client.force_authenticate(
            user=self.education_officer
        )

        school_response = self.client.get(
            reverse("education-report-list"),
            {"school": self.school.id},
        )

        self.assertEqual(
            school_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(school_response.data),
            1,
        )

        classroom_response = self.client.get(
            reverse("education-report-list"),
            {"classroom": self.classroom.id},
        )

        self.assertEqual(
            classroom_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(classroom_response.data),
            1,
        )

    def test_education_officer_can_filter_reports_by_date_range(self):
        first_session = timezone.now() - timedelta(days=10)
        second_session = timezone.now() - timedelta(days=2)

        SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=first_session,
            lesson_summary="Old report",
            present_count=10,
            absent_count=1,
            submitted_at=first_session + timedelta(hours=1),
        )

        SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=second_session,
            lesson_summary="Recent report",
            present_count=8,
            absent_count=2,
            submitted_at=second_session + timedelta(hours=1),
        )

        self.client.force_authenticate(
            user=self.education_officer
        )

        start_date = (
            timezone.now() - timedelta(days=5)
        ).date().isoformat()

        end_date = timezone.now().date().isoformat()

        response = self.client.get(
            reverse("education-report-list"),
            {
                "start_date": start_date,
                "end_date": end_date,
            },
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
            "Recent report",
        )

    def test_education_officer_can_approve_report(self):
        report = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Django REST Framework",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
        )

        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.patch(
            reverse(
                "session-report-review",
                kwargs={"pk": report.pk},
            ),
            {
                "status": SessionReport.Status.APPROVED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            SessionReport.Status.APPROVED,
        )

        self.assertIsNone(
            report.rejection_reason,
        )

    def test_education_officer_can_reject_report_with_reason(self):
        report = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Django REST Framework",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
        )

        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.patch(
            reverse(
                "session-report-review",
                kwargs={"pk": report.pk},
            ),
            {
                "status": SessionReport.Status.REJECTED,
                "rejection_reason": "Lesson summary needs more details.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            SessionReport.Status.REJECTED,
        )

        self.assertEqual(
            report.rejection_reason,
            "Lesson summary needs more details.",
        )

    def test_education_officer_cannot_reject_report_without_reason(self):
        report = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Django REST Framework",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
        )

        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.patch(
            reverse(
                "session-report-review",
                kwargs={"pk": report.pk},
            ),
            {
                "status": SessionReport.Status.REJECTED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        report.refresh_from_db()

        # گزارش باید همچنان pending باقی مانده باشد
        self.assertEqual(
            report.status,
            SessionReport.Status.PENDING,
        )

    def test_teacher_cannot_review_own_report(self):
        report = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Django REST Framework",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
        )

        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.patch(
            reverse(
                "session-report-review",
                kwargs={"pk": report.pk},
            ),
            {
                "status": SessionReport.Status.APPROVED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            SessionReport.Status.PENDING,
        )

    def test_finance_officer_cannot_review_report(self):
        report = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Django REST Framework",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
        )

        self.client.force_authenticate(
            user=self.finance_officer
        )

        response = self.client.patch(
            reverse(
                "session-report-review",
                kwargs={"pk": report.pk},
            ),
            {
                "status": SessionReport.Status.APPROVED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            SessionReport.Status.PENDING,
        )

    def test_teacher_can_edit_rejected_report_and_resubmit(self):
        report = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Old summary",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
            status=SessionReport.Status.REJECTED,
            rejection_reason="Needs more details.",
        )

        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.patch(
            reverse(
                "session-report-update",
                kwargs={"pk": report.pk},
            ),
            {
                "lesson_summary": "Updated and more detailed summary",
                "present_count": 11,
                "absent_count": 1,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.lesson_summary,
            "Updated and more detailed summary",
        )

        self.assertEqual(
            report.status,
            SessionReport.Status.PENDING,
        )

        self.assertIsNone(
            report.rejection_reason,
        )

    def test_teacher_cannot_edit_pending_report(self):
        report = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Pending report",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
            status=SessionReport.Status.PENDING,
        )

        self.client.force_authenticate(user=self.teacher)

        response = self.client.patch(
            reverse(
                "session-report-update",
                kwargs={"pk": report.pk},
            ),
            {
                "lesson_summary": "Changed summary",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.lesson_summary,
            "Pending report",
        )

    def test_teacher_cannot_edit_approved_report(self):
        report = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Approved report",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
            status=SessionReport.Status.APPROVED,
        )

        self.client.force_authenticate(user=self.teacher)

        response = self.client.patch(
            reverse(
                "session-report-update",
                kwargs={"pk": report.pk},
            ),
            {
                "lesson_summary": "Changed summary",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.lesson_summary,
            "Approved report",
        )

    def test_education_officer_cannot_change_report_content(self):
        report = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Original summary",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
        )

        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.patch(
            reverse(
                "session-report-review",
                kwargs={"pk": report.pk},
            ),
            {
                "status": SessionReport.Status.APPROVED,
                "lesson_summary": "Changed by education officer",
                "present_count": 99,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            SessionReport.Status.APPROVED,
        )

        self.assertEqual(
            report.lesson_summary,
            "Original summary",
        )

        self.assertEqual(
            report.present_count,
            10,
        )

    def test_education_officer_cannot_change_report_content(self):
        report = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Original summary",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
        )

        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.patch(
            reverse(
                "session-report-review",
                kwargs={"pk": report.pk},
            ),
            {
                "status": SessionReport.Status.APPROVED,
                "lesson_summary": "Changed by education officer",
                "present_count": 99,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            SessionReport.Status.APPROVED,
        )

        self.assertEqual(
            report.lesson_summary,
            "Original summary",
        )

        self.assertEqual(
            report.present_count,
            10,
        )

    def test_late_report_is_automatically_marked_as_late(self):
        assignment = TeacherAssignment.objects.get(
            teacher=self.teacher,
            classroom=self.classroom,
        )

        assignment.start_date = (
            timezone.now() - timedelta(days=10)
        ).date()

        assignment.save()

        self.client.force_authenticate(user=self.teacher)

        session_time = timezone.now() - timedelta(hours=49)

        response = self.client.post(
            reverse("session-report-list-create"),
            {
                "classroom": self.classroom.id,
                "session_date": session_time.isoformat(),
                "lesson_summary": "Late session report",
                "present_count": 10,
                "absent_count": 2,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        report = SessionReport.objects.get(
            pk=response.data["id"]
        )

        self.assertTrue(report.is_late)
        self.assertIsNotNone(report.submitted_at)

    def test_on_time_report_is_not_marked_as_late(self):
        assignment = TeacherAssignment.objects.get(
            teacher=self.teacher,
            classroom=self.classroom,
        )

        assignment.start_date = (
            timezone.now() - timedelta(days=10)
        ).date()

        assignment.save()

        self.client.force_authenticate(user=self.teacher)

        session_time = timezone.now() - timedelta(hours=47)

        response = self.client.post(
            reverse("session-report-list-create"),
            {
                "classroom": self.classroom.id,
                "session_date": session_time.isoformat(),
                "lesson_summary": "On time session report",
                "present_count": 10,
                "absent_count": 2,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        report = SessionReport.objects.get(
            pk=response.data["id"]
        )

        self.assertFalse(report.is_late)

    def test_teacher_cannot_set_system_fields_when_creating_report(self):
        self.client.force_authenticate(user=self.teacher)

        session_time = timezone.now()

        response = self.client.post(
            reverse("session-report-list-create"),
            {
                "classroom": self.classroom.id,
                "session_date": session_time.isoformat(),
                "lesson_summary": "Django REST Framework",
                "present_count": 10,
                "absent_count": 2,

                # Teacher tries to manipulate system fields
                "status": SessionReport.Status.APPROVED,
                "is_late": True,
                "rejection_reason": "Fake reason",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        report = SessionReport.objects.get(
            pk=response.data["id"]
        )

        # System must control these values
        self.assertEqual(
            report.status,
            SessionReport.Status.PENDING,
        )

        self.assertFalse(report.is_late)

        self.assertIsNone(
            report.rejection_reason,
        )

        self.assertEqual(
            report.teacher,
            self.teacher,
        )

    def test_teacher_cannot_change_system_fields_when_resubmitting_report(self):
        report = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Old summary",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
            status=SessionReport.Status.REJECTED,
            rejection_reason="Needs more details.",
        )

        original_submitted_at = report.submitted_at

        self.client.force_authenticate(user=self.teacher)

        response = self.client.patch(
            reverse(
                "session-report-update",
                kwargs={"pk": report.pk},
            ),
            {
                "lesson_summary": "Updated summary",

                # Teacher tries to manipulate system fields
                "status": SessionReport.Status.APPROVED,
                "is_late": True,
                "submitted_at": (
                    timezone.now() - timedelta(days=10)
                ).isoformat(),
                "rejection_reason": "Fake reason",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.lesson_summary,
            "Updated summary",
        )

        # Resubmission must always return to pending
        self.assertEqual(
            report.status,
            SessionReport.Status.PENDING,
        )

        # Teacher cannot manipulate these fields
        self.assertFalse(report.is_late)

        self.assertIsNone(
            report.rejection_reason,
        )

        self.assertEqual(
            report.submitted_at,
            original_submitted_at,
        )

    def test_teacher_monthly_summary(self):
        self.client.force_authenticate(user=self.teacher)

        SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.make_aware(
                timezone.datetime(2026, 8, 5, 10, 0)
            ),
            lesson_summary="Pending report",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
            status=SessionReport.Status.PENDING,
        )

        SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.make_aware(
                timezone.datetime(2026, 8, 10, 10, 0)
            ),
            lesson_summary="Approved report",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
            status=SessionReport.Status.APPROVED,
        )

        SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.make_aware(
                timezone.datetime(2026, 8, 15, 10, 0)
            ),
            lesson_summary="Rejected report",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
            status=SessionReport.Status.REJECTED,
            rejection_reason="Needs more details",
        )

        url = reverse("teacher-monthly-report-summary")

        response = self.client.get(
            url,
            {
                "year": 2026,
                "month": 8,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(response.data["year"], 2026)
        self.assertEqual(response.data["month"], 8)
        self.assertEqual(response.data["total"], 3)
        self.assertEqual(response.data["pending"], 1)
        self.assertEqual(response.data["approved"], 1)
        self.assertEqual(response.data["rejected"], 1)

    def test_monthly_summary_requires_year(self):
        self.client.force_authenticate(user=self.teacher)

        url = reverse("teacher-monthly-report-summary")

        response = self.client.get(
            url,
            {
                "month": 8,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_monthly_summary_requires_month(self):
        self.client.force_authenticate(user=self.teacher)

        url = reverse("teacher-monthly-report-summary")

        response = self.client.get(
            url,
            {
                "year": 2026,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_education_officer_cannot_access_monthly_summary(self):
        self.client.force_authenticate(user=self.education_officer)

        url = reverse("teacher-monthly-report-summary")

        response = self.client.get(
            url,
            {
                "year": 2026,
                "month": 8,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_education_officer_can_approve_reports_in_group(self):
        report1 = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Report 1",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
            status=SessionReport.Status.PENDING,
        )

        report2 = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Report 2",
            present_count=8,
            absent_count=1,
            submitted_at=timezone.now(),
            status=SessionReport.Status.PENDING,
        )

        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.post(
            reverse("group-approve"),
            {
                "report_ids": [
                    report1.id,
                    report2.id,
                ]
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["approved_count"],
            2,
        )

        report1.refresh_from_db()
        report2.refresh_from_db()

        self.assertEqual(
            report1.status,
            SessionReport.Status.APPROVED,
        )

        self.assertEqual(
            report2.status,
            SessionReport.Status.APPROVED,
        )

    def test_teacher_cannot_approve_reports_in_group(self):
        report = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Report",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
            status=SessionReport.Status.PENDING,
        )

        self.client.force_authenticate(user=self.teacher)

        response = self.client.post(
            reverse("group-approve"),
            {
                "report_ids": [report.id]
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_group_approve_requires_report_ids(self):
        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.post(
            reverse("group-approve"),
            {
                "report_ids": []
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


    def test_reject_report_creates_status_history(self):
        report = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Django REST Framework",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
            status=SessionReport.Status.PENDING,
        )

        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.patch(
            reverse(
                "session-report-review",
                kwargs={"pk": report.pk},
            ),
            {
                "status": SessionReport.Status.REJECTED,
                "rejection_reason": "Needs more details.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        history = SessionReportStatusHistory.objects.get(
            report=report
        )

        self.assertEqual(
            history.status,
            SessionReport.Status.REJECTED,
        )

        self.assertEqual(
            history.changed_by,
            self.education_officer,
        )

        self.assertEqual(
            history.note,
            "Needs more details.",
        )

    def test_resubmit_report_creates_status_history(self):
        report = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Old summary",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
            status=SessionReport.Status.REJECTED,
            rejection_reason="Needs more details.",
        )

        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.patch(
            reverse(
                "session-report-update",
                kwargs={"pk": report.pk},
            ),
            {
                "lesson_summary": "Updated summary",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        history = SessionReportStatusHistory.objects.get(
            report=report
        )

        self.assertEqual(
            history.status,
            SessionReport.Status.PENDING,
        )

        self.assertEqual(
            history.changed_by,
            self.teacher,
        )

    def test_group_approve_creates_status_history(self):
        report1 = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Report 1",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
            status=SessionReport.Status.PENDING,
        )

        report2 = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Report 2",
            present_count=8,
            absent_count=1,
            submitted_at=timezone.now(),
            status=SessionReport.Status.PENDING,
        )

        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.post(
            reverse("group-approve"),
            {
                "report_ids": [
                    report1.id,
                    report2.id,
                ]
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            SessionReportStatusHistory.objects.filter(
                status=SessionReport.Status.APPROVED
            ).count(),
            2,
        )

    def test_teacher_can_view_own_report_history(self):
        report = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Report",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
        )

        SessionReportStatusHistory.objects.create(
            report=report,
            status=SessionReport.Status.REJECTED,
            changed_by=self.education_officer,
            note="Needs more details.",
        )

        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(
            reverse(
                "session-report-history",
                kwargs={"pk": report.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_teacher_cannot_view_another_teacher_report_history(self):
        other_teacher = User.objects.create_user(
            username="history_teacher",
            password="1234",
            role=User.Role.TEACHER,
            phone_number="09160000020",
            emergency_phone="09160000021",
        )

        report = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Report",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
        )

        self.client.force_authenticate(user=other_teacher)

        response = self.client.get(
            reverse(
                "session-report-history",
                kwargs={"pk": report.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_education_officer_can_view_report_history(self):
        report = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Report",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
        )

        SessionReportStatusHistory.objects.create(
            report=report,
            status=SessionReport.Status.APPROVED,
            changed_by=self.education_officer,
        )

        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.get(
            reverse(
                "session-report-history",
                kwargs={"pk": report.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )



    def test_calculate_is_late_without_submitted_at(self):
        report = SessionReport(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Test",
            present_count=10,
            absent_count=2,
            submitted_at=None,
        )

        self.assertFalse(
            report.calculate_is_late()
        )


    def test_submit_sets_report_fields(self):
        report = SessionReport(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Test",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
            status=SessionReport.Status.REJECTED,
            rejection_reason="Old reason",
        )

        report.submit()

        self.assertIsNotNone(report.submitted_at)
        self.assertEqual(
            report.status,
            SessionReport.Status.PENDING,
        )
        self.assertIsNone(
            report.rejection_reason,
        )


    def test_rejected_report_requires_rejection_reason(self):
        report = SessionReport(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Test",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
            status=SessionReport.Status.REJECTED,
            rejection_reason=None,
        )

        with self.assertRaises(ValidationError):
            report.full_clean()


    def test_session_report_str(self):
        report = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Test",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
        )

        self.assertIn(
            str(self.classroom),
            str(report),
        )


    def test_status_history_str(self):
        report = SessionReport.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            session_date=timezone.now(),
            lesson_summary="Test",
            present_count=10,
            absent_count=2,
            submitted_at=timezone.now(),
        )

        history = SessionReportStatusHistory.objects.create(
            report=report,
            status=SessionReport.Status.APPROVED,
            changed_by=self.education_officer,
        )

        self.assertEqual(
            str(history),
            f"{report.id} - approved",
        )