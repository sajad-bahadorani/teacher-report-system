from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import User


class UserModelTest(TestCase):

    def test_create_teacher(self):
        user = User.objects.create_user(
            username="teacher1",
            password="1234",
            role=User.Role.TEACHER,
            phone_number="09123456789",
            emergency_phone="09999999999",
        )

        self.assertEqual(user.role, User.Role.TEACHER)
        
    def test_create_education_officer(self):
        user = User.objects.create_user(
            username="education1",
            password="1234",
            role=User.Role.EDUCATION_OFFICER,
            phone_number="09111111111",
            emergency_phone="09222222222",
        )

        self.assertEqual(user.role, User.Role.EDUCATION_OFFICER)
        
    def test_create_finance_officer(self):
        user = User.objects.create_user(
            username="finance1",
            password="1234",
            role=User.Role.FINANCE_OFFICER,
            phone_number="09333333333",
            emergency_phone="09444444444",
        )

        self.assertEqual(user.role, User.Role.FINANCE_OFFICER)


class LoginTest(APITestCase):

    def test_teacher_can_login(self):
        User.objects.create_user(
            username="teacher",
            password="1234",
            role=User.Role.TEACHER,
            phone_number="09111111111",
            emergency_phone="09222222222",
        )

        response = self.client.post(
            "/api/accounts/login/",
            {
                "username": "teacher",
                "password": "1234",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)


class ProfileTest(APITestCase):

    def test_teacher_can_see_profile(self):
        user = User.objects.create_user(
            username="teacher",
            password="1234",
            role=User.Role.TEACHER,
            phone_number="09111111111",
            emergency_phone="09222222222",
        )

        login = self.client.post(
            "/api/accounts/login/",
            {
                "username": "teacher",
                "password": "1234",
            },
            format="json",
        )

        token = login.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        response = self.client.get("/api/accounts/me/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "teacher")
        self.assertEqual(response.data["role"], User.Role.TEACHER)


class ProfilePermissionTest(APITestCase):

    def test_guest_cannot_see_profile(self):
        response = self.client.get("/api/accounts/me/")

        self.assertEqual(response.status_code, 401)
        