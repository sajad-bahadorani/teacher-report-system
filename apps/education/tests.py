from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User

from .models import Classroom, School, TeacherAssignment, Term
from .serializers import (
    SchoolSerializer,
    TermSerializer,
    ClassroomSerializer,
    TeacherAssignmentSerializer,
)

class SchoolTest(TestCase):

    def test_create_school(self):
        school = School.objects.create(
            name="Sample School"
        )

        self.assertEqual(
            school.name,
            "Sample School"
        )

    def test_school_serializer(self):
        school = School.objects.create(
            name="Sample School"
        )

        serializer = SchoolSerializer(school)

        self.assertEqual(
            serializer.data["name"],
            "Sample School"
        )


class TermTest(TestCase):

    def test_create_term(self):
        term = Term.objects.create(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
            term_type=Term.TermType.NORMAL
        )

        self.assertEqual(
            term.term_type,
            Term.TermType.NORMAL
        )


    def test_term_end_date_before_start_date(self):

        term = Term(
            start_date=date(2026, 5, 1),
            end_date=date(2026, 1, 1),
            term_type=Term.TermType.NORMAL
        )

        with self.assertRaises(ValidationError):
            term.full_clean()

    def test_term_serializer_rejects_invalid_date_range(self):
        data = {
            "start_date": "2026-05-01",
            "end_date": "2026-01-01",
            "term_type": Term.TermType.NORMAL,
        }

        serializer = TermSerializer(data=data)

        self.assertFalse(serializer.is_valid())


class ClassroomTest(TestCase):

    def setUp(self):

        self.school = School.objects.create(
            name="Sample School"
        )

        self.term = Term.objects.create(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
            term_type=Term.TermType.NORMAL
        )


    def test_create_classroom(self):

        classroom = Classroom.objects.create(
            school=self.school,
            term=self.term,
            session_duration=90
        )

        self.assertEqual(
            classroom.session_duration,
            90
        )


    def test_invalid_session_duration(self):

        classroom = Classroom(
            school=self.school,
            term=self.term,
            session_duration=45
        )

        with self.assertRaises(ValidationError):
            classroom.full_clean()

    def test_classroom_serializer_rejects_invalid_session_duration(self):
        data = {
            "school": self.school.id,
            "term": self.term.id,
            "session_duration": 45,
        }

        serializer = ClassroomSerializer(data=data)

        self.assertFalse(serializer.is_valid())



class TeacherAssignmentTest(TestCase):

    def setUp(self):
        self.teacher1 = User.objects.create_user(
            username="teacher1",
            password="1234",
            role=User.Role.TEACHER,
            phone_number="09111111111",
            emergency_phone="09222222222",
        )

        self.teacher2 = User.objects.create_user(
            username="teacher2",
            password="1234",
            role=User.Role.TEACHER,
            phone_number="09222222222",
            emergency_phone="09333333333",
        )

        self.education_officer = User.objects.create_user(
            username="education1",
            password="1234",
            role=User.Role.EDUCATION_OFFICER,
            phone_number="09333333333",
            emergency_phone="09444444444",
        )

        self.school = School.objects.create(
            name="Sample School"
        )

        self.term = Term.objects.create(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
            term_type=Term.TermType.NORMAL,
        )

        self.classroom = Classroom.objects.create(
            school=self.school,
            term=self.term,
            session_duration=90,
        )

    def test_teacher_assignments_can_have_non_overlapping_date_ranges(self):
        assignment1 = TeacherAssignment.objects.create(
            teacher=self.teacher1,
            classroom=self.classroom,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
        )

        assignment2 = TeacherAssignment.objects.create(
            teacher=self.teacher2,
            classroom=self.classroom,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 3, 31),
        )

        self.assertEqual(
            TeacherAssignment.objects.filter(
                classroom=self.classroom
            ).count(),
            2
        )

        self.assertEqual(
            assignment1.teacher,
            self.teacher1
        )

        self.assertEqual(
            assignment2.teacher,
            self.teacher2
        )

    def test_assignment_end_date_before_start_date(self):
        assignment = TeacherAssignment(
            teacher=self.teacher1,
            classroom=self.classroom,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 1, 1),
        )

        with self.assertRaises(ValidationError):
            assignment.full_clean()


    def test_assignment_cannot_start_before_term(self):
        assignment = TeacherAssignment(
            teacher=self.teacher1,
            classroom=self.classroom,
            start_date=date(2025, 12, 25),
            end_date=date(2026, 1, 31),
        )

        with self.assertRaises(ValidationError):
            assignment.full_clean()

    def test_only_teacher_can_be_assigned(self):
        assignment = TeacherAssignment(
            teacher=self.education_officer,
            classroom=self.classroom,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
        )

        with self.assertRaises(ValidationError):
            assignment.full_clean()


    def test_assignment_cannot_end_after_term(self):
        assignment = TeacherAssignment(
            teacher=self.teacher1,
            classroom=self.classroom,
            start_date=date(2026, 3, 1),
            end_date=date(2026, 4, 10),
        )

        with self.assertRaises(ValidationError):
            assignment.full_clean()

    def test_teacher_assignments_cannot_overlap(self):
        TeacherAssignment.objects.create(
            teacher=self.teacher1,
            classroom=self.classroom,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
        )

        assignment2 = TeacherAssignment(
            teacher=self.teacher2,
            classroom=self.classroom,
            start_date=date(2026, 1, 15),
            end_date=date(2026, 2, 15),
        )

        with self.assertRaises(ValidationError):
            assignment2.full_clean()


    def test_assignment_can_have_no_end_date(self):
        assignment = TeacherAssignment(
            teacher=self.teacher1,
            classroom=self.classroom,
            start_date=date(2026, 1, 1),
            end_date=None,
        )

        assignment.full_clean()


    def test_open_ended_assignment_cannot_overlap(self):
        TeacherAssignment.objects.create(
            teacher=self.teacher1,
            classroom=self.classroom,
            start_date=date(2026, 1, 1),
            end_date=None,
        )

        assignment2 = TeacherAssignment(
            teacher=self.teacher2,
            classroom=self.classroom,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 3, 1),
        )

        with self.assertRaises(ValidationError):
            assignment2.full_clean()

    def test_updating_assignment_does_not_overlap_with_itself(self):
        assignment = TeacherAssignment.objects.create(
            teacher=self.teacher1,
            classroom=self.classroom,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
        )

        assignment.end_date = date(2026, 2, 15)

        assignment.full_clean()

    def test_teacher_assignment_serializer(self):
        assignment = TeacherAssignment.objects.create(
            teacher=self.teacher1,
            classroom=self.classroom,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
        )

        serializer = TeacherAssignmentSerializer(assignment)

        self.assertEqual(
            serializer.data["teacher"],
            self.teacher1.id
        )

        self.assertEqual(
            serializer.data["classroom"],
            self.classroom.id
        )

    def test_teacher_assignment_serializer_rejects_non_teacher(self):
        data = {
            "teacher": self.education_officer.id,
            "classroom": self.classroom.id,
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
        }

        serializer = TeacherAssignmentSerializer(data=data)

        self.assertFalse(serializer.is_valid())


    def test_teacher_assignment_serializer_rejects_end_date_before_start_date(self):
        data = {
            "teacher": self.teacher1.id,
            "classroom": self.classroom.id,
            "start_date": "2026-02-01",
            "end_date": "2026-01-01",
        }

        serializer = TeacherAssignmentSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_teacher_assignment_serializer_rejects_start_before_term(self):
        data = {
            "teacher": self.teacher1.id,
            "classroom": self.classroom.id,
            "start_date": "2025-12-25",
            "end_date": "2026-01-31",
        }

        serializer = TeacherAssignmentSerializer(data=data)

        self.assertFalse(serializer.is_valid())


    def test_teacher_assignment_serializer_rejects_end_after_term(self):
        data = {
            "teacher": self.teacher1.id,
            "classroom": self.classroom.id,
            "start_date": "2026-03-01",
            "end_date": "2026-04-10",
        }

        serializer = TeacherAssignmentSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_teacher_assignment_serializer_rejects_overlap(self):
        TeacherAssignment.objects.create(
            teacher=self.teacher1,
            classroom=self.classroom,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
        )

        data = {
            "teacher": self.teacher2.id,
            "classroom": self.classroom.id,
            "start_date": "2026-01-15",
            "end_date": "2026-02-15",
        }

        serializer = TeacherAssignmentSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_teacher_assignment_serializer_update_does_not_overlap_with_itself(self):
        assignment = TeacherAssignment.objects.create(
            teacher=self.teacher1,
            classroom=self.classroom,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
        )

        data = {
            "teacher": self.teacher1.id,
            "classroom": self.classroom.id,
            "start_date": "2026-01-01",
            "end_date": "2026-02-15",
        }

        serializer = TeacherAssignmentSerializer(
            assignment,
            data=data,
        )

        self.assertTrue(serializer.is_valid())

        updated_assignment = serializer.save()

        self.assertEqual(
            updated_assignment.end_date,
            date(2026, 2, 15)
        )

    def test_teacher_assignment_serializer_partial_update_rejects_overlap(self):
        assignment1 = TeacherAssignment.objects.create(
            teacher=self.teacher1,
            classroom=self.classroom,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
        )

        assignment2 = TeacherAssignment.objects.create(
            teacher=self.teacher2,
            classroom=self.classroom,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 3, 31),
        )

        data = {
            "start_date": "2026-01-15"
        }

        serializer = TeacherAssignmentSerializer(
            assignment2,
            data=data,
            partial=True,
        )

        self.assertFalse(serializer.is_valid())


class SchoolAPITest(APITestCase):

    def setUp(self):
        self.education_officer = User.objects.create_user(
            username="education1",
            password="1234",
            role=User.Role.EDUCATION_OFFICER,
            phone_number="09120000001",
            emergency_phone="09120000002",
        )

        self.client.force_authenticate(
            user=self.education_officer
        )

        self.teacher = User.objects.create_user(
            username="teacher_school",
            password="1234",
            role=User.Role.TEACHER,
            phone_number="09120000003",
            emergency_phone="09120000004",
        )

        self.finance_officer = User.objects.create_user(
            username="finance_school",
            password="1234",
            role=User.Role.FINANCE_OFFICER,
            phone_number="09120000005",
            emergency_phone="09120000006",
        )

    def test_education_officer_can_create_school(self):
        data = {
            "name": "Maktab School"
        }

        response = self.client.post(
            reverse("school-list-create"),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            School.objects.filter(name="Maktab School").exists()
        )

    def test_education_officer_can_list_schools(self):
        School.objects.create(name="School 1")
        School.objects.create(name="School 2")

        response = self.client.get(
            reverse("school-list-create")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

    def test_education_officer_can_update_school(self):
        school = School.objects.create(
            name="Old School"
        )

        data = {
            "name": "New School"
        }

        response = self.client.patch(
            reverse(
                "school-update",
                kwargs={"pk": school.pk},
            ),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        school.refresh_from_db()

        self.assertEqual(
            school.name,
            "New School",
        )

    def test_teacher_cannot_create_school(self):
        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.post(
            reverse("school-list-create"),
            {"name": "Forbidden School"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
            School.objects.filter(
                name="Forbidden School"
            ).exists()
        )

    def test_finance_officer_cannot_create_school(self):
        self.client.force_authenticate(
            user=self.finance_officer
        )

        response = self.client.post(
            reverse("school-list-create"),
            {"name": "Forbidden School"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )


class TermAPITest(APITestCase):

    def setUp(self):
        self.education_officer = User.objects.create_user(
            username="education_term",
            password="1234",
            role=User.Role.EDUCATION_OFFICER,
            phone_number="09130000001",
            emergency_phone="09130000002",
        )

        self.client.force_authenticate(
            user=self.education_officer
        )

        self.teacher = User.objects.create_user(
            username="teacher_term",
            password="1234",
            role=User.Role.TEACHER,
            phone_number="09130000003",
            emergency_phone="09130000004",
        )

        self.finance_officer = User.objects.create_user(
            username="finance_term",
            password="1234",
            role=User.Role.FINANCE_OFFICER,
            phone_number="09130000005",
            emergency_phone="09130000006",
        )

    def test_education_officer_can_create_term(self):
        data = {
            "start_date": "2026-01-01",
            "end_date": "2026-03-31",
            "term_type": Term.TermType.NORMAL,
        }

        response = self.client.post(
            reverse("term-list-create"),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Term.objects.filter(
                start_date=date(2026, 1, 1),
                end_date=date(2026, 3, 31),
                term_type=Term.TermType.NORMAL,
            ).exists()
        )

    def test_education_officer_can_list_terms(self):
        Term.objects.create(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
            term_type=Term.TermType.NORMAL,
        )

        Term.objects.create(
            start_date=date(2026, 6, 1),
            end_date=date(2026, 8, 31),
            term_type=Term.TermType.SUMMER,
        )

        response = self.client.get(
            reverse("term-list-create")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

    def test_term_api_rejects_invalid_date_range(self):
        data = {
            "start_date": "2026-05-01",
            "end_date": "2026-01-01",
            "term_type": Term.TermType.NORMAL,
        }

        response = self.client.post(
            reverse("term-list-create"),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_teacher_cannot_create_term(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post(
            reverse("term-list-create"),
            {
                "start_date": "2026-01-01",
                "end_date": "2026-03-31",
                "term_type": Term.TermType.NORMAL,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )


    def test_finance_officer_cannot_create_term(self):
        self.client.force_authenticate(user=self.finance_officer)

        response = self.client.post(
            reverse("term-list-create"),
            {
                "start_date": "2026-01-01",
                "end_date": "2026-03-31",
                "term_type": Term.TermType.NORMAL,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_education_officer_can_update_term(self):
        term = Term.objects.create(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
            term_type=Term.TermType.NORMAL,
        )

        response = self.client.patch(
            reverse(
                "term-update",
                kwargs={"pk": term.pk},
            ),
            {
                "term_type": Term.TermType.SUMMER,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        term.refresh_from_db()

        self.assertEqual(
            term.term_type,
            Term.TermType.SUMMER,
        )


class ClassroomAPITest(APITestCase):

    def setUp(self):
        self.education_officer = User.objects.create_user(
            username="education_classroom",
            password="1234",
            role=User.Role.EDUCATION_OFFICER,
            phone_number="09140000001",
            emergency_phone="09140000002",
        )

        self.school = School.objects.create(
            name="Sample School"
        )

        self.term = Term.objects.create(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
            term_type=Term.TermType.NORMAL,
        )

        self.client.force_authenticate(
            user=self.education_officer
        )

    def test_education_officer_can_create_classroom(self):
        data = {
            "school": self.school.id,
            "term": self.term.id,
            "session_duration": 90,
        }

        response = self.client.post(
            reverse("classroom-list-create"),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Classroom.objects.filter(
                school=self.school,
                term=self.term,
                session_duration=90,
            ).exists()
        )

    def test_classroom_api_rejects_invalid_session_duration(self):
        data = {
            "school": self.school.id,
            "term": self.term.id,
            "session_duration": 45,
        }

        response = self.client.post(
            reverse("classroom-list-create"),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )