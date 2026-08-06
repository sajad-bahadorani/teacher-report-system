from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import School, Term, Classroom


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