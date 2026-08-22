from decimal import Decimal

from apps.reports.models import SessionReport

from .models import SalaryRate


def calculate_teacher_monthly_salary(teacher, year, month):
    reports = SessionReport.objects.filter(
        teacher=teacher,
        session_date__year=year,
        session_date__month=month,
        status=SessionReport.Status.APPROVED,
        is_late=False,
    )

    total_wage = Decimal("0")

    for report in reports:
        term = report.classroom.term

        salary_rate = SalaryRate.objects.get(teacher=teacher, term=term)

        base_rate = salary_rate.base_rate
        duration = report.classroom.session_duration

        if duration == 90:
            session_wage = base_rate

        elif duration == 60:
            session_wage = base_rate * Decimal("0.7")

        elif duration == 120:
            session_wage = base_rate * Decimal("1.3")

        else:
            continue

        if term.term_type == term.TermType.SUMMER:
            session_wage = session_wage * Decimal("1.1")

        total_wage += session_wage

    return total_wage