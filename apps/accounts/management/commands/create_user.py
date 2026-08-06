from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):
    help = "Create a new user with a specific role"

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--role", required=True)
        parser.add_argument("--first_name", default="")
        parser.add_argument("--last_name", default="")
        parser.add_argument("--phone_number", required=True)
        parser.add_argument("--emergency_phone", required=True)

    def handle(self, *args, **options):

        if options["role"] not in [choice[0] for choice in User.Role.choices]:
            raise CommandError("Invalid role.")

        if User.objects.filter(username=options["username"]).exists():
            raise CommandError("Username already exists.")

        user = User.objects.create_user(
            username=options["username"],
            password=options["password"],
            role=options["role"],
            first_name=options["first_name"],
            last_name=options["last_name"],
            phone_number=options["phone_number"],
            emergency_phone=options["emergency_phone"],
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"User '{user.username}' created successfully."
            )
        )