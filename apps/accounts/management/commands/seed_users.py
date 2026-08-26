from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        users = [
            {
                "username": "teacher_demo",
                "password": "1234",
                "first_name": "Demo",
                "last_name": "Teacher",
                "phone_number": "09100000001",
                "emergency_phone": "09100000002",
                "role": User.Role.TEACHER,
            },
            {
                "username": "education_demo",
                "password": "1234",
                "first_name": "Demo",
                "last_name": "Education",
                "phone_number": "09100000003",
                "emergency_phone": "09100000004",
                "role": User.Role.EDUCATION_OFFICER,
            },
            {
                "username": "finance_demo",
                "password": "1234",
                "first_name": "Demo",
                "last_name": "Finance",
                "phone_number": "09100000005",
                "emergency_phone": "09100000006",
                "role": User.Role.FINANCE_OFFICER,
            },
        ]

        for data in users:
            password = data.pop("password")

            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults=data,
            )

            if created:
                user.set_password(password)
                user.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created {user.username}"
                    )
                )
            else:
                self.stdout.write(
                    f"{user.username} already exists."
                )