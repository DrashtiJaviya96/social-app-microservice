from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import UserProfile


class UserProfileAPITest(APITestCase):
    def setUp(self):
        self.auth_user = User.objects.create_user(
            username="john123",
            email="john@example.com",
            password="Xk9$vLm2qP",
            first_name="John",
            last_name="Doe",
        )
        self.user = UserProfile.objects.create(user=self.auth_user)
        self.client.force_authenticate(user=self.auth_user) 

    def test_list_users(self):
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user(self):
        url = reverse("register")
        data = {
            "username": "john125",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john1@example.com",
            "password": "Xk9$vLm2qP"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_user_detail(self):
        url = reverse("user-detail", kwargs={"pk": self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user(self):
        url = reverse("user-update", kwargs={"pk": self.user.id})
        response = self.client.patch(url, {"username": "newname"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user(self):
        url = reverse("user-delete", kwargs={"pk": self.user.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)