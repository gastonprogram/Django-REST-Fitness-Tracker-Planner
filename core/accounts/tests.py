from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthTests(APITestCase):
    def test_register_and_login(self):
        # Register
        response = self.client.post(reverse("register"), {
            "username": "testuser",
            "email": "test@test.com",
            "password": "StrongPass123!",
        })
        self.assertEqual(response.status_code, 201)

        # Login
        response = self.client.post(reverse("login"), {
            "email": "test@test.com",
            "password": "StrongPass123!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

