from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import User
from .models import School, Term, Classroom, TeacherAssignment


class SchoolTest(TestCase):

    def test_create_school(self):
        school = School.objects.create(
            name="Sample School"
        )

        self.assertEqual(
            school.name,
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