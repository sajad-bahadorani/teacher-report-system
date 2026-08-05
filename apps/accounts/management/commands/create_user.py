from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand



class Command(BaseCommand):
    help = "Create a new user"

    def add_arguments(self, parser):
        parser.add_argument("--role",choices=["teacher", "education", "finance"], required=True)

    def handle(self, *args, **options):
        User = get_user_model()
        

        username = input("Username: ")
        password = input("Password: ")
        first_name = input("First name: ")
        last_name = input("Last name: ")
        phone_number = input("Phone number: ")
        emergency_phone = input("Emergency phone: ")

        User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            emergency_phone=emergency_phone,
            role=options["role"],
        )

        self.stdout.write(
            self.style.SUCCESS("User created successfully.")
        )