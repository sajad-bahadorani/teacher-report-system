from getpass import getpass

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("--role", required=True)

        parser.add_argument("--username")
        parser.add_argument("--password")
        parser.add_argument("--first_name")
        parser.add_argument("--last_name")
        parser.add_argument("--phone_number")
        parser.add_argument("--emergency_phone")

    def handle(self, *args, **options):

        role = options["role"]

        if role not in [choice[0] for choice in User.Role.choices]:
            raise CommandError("Invalid role.")

        username = options["username"] or input("Username: ").strip()

        if User.objects.filter(username=username).exists():
            raise CommandError("Username already exists.")

        first_name = options["first_name"] or input("First name: ").strip()

        last_name = options["last_name"] or input("Last name: ").strip()

        phone_number = options["phone_number"] or input("Phone number: ").strip()

        if User.objects.filter(phone_number=phone_number).exists():
            raise CommandError("Phone number already exists.")

        emergency_phone = (
            options["emergency_phone"]
            or input("Emergency phone: ").strip()
        )

        password = options["password"] or getpass("Password: ")

        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            emergency_phone=emergency_phone,
            role=role,
        )

        user.set_password(password)

        try:
            user.full_clean()
        except ValidationError as e:
            raise CommandError(e)

        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"User '{user.username}' created successfully."
            )
        )