from unittest.mock import patch, Mock
from django.test import TestCase # non-API Django tests like Custome funciton , serializers without DRF 
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase #DRF API endpoint tests
from .models import Post
from django.contrib.auth.models import User


class PostAPITest(APITestCase):
    def setUp(self):
        self.auth_user = User.objects.create_user(      
            username="john123", password="Xk9$vLm2qP"
        )
        self.client.force_authenticate(user=self.auth_user)
        self.post = Post.objects.create(
            title="Hello",
            content="Hello content",
            author_user_id=1
        )

    def test_list_posts(self):
        url = reverse("posts")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_post_detail(self):
        url = reverse("post-detail", kwargs={"pk": self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("posts.serializers.requests.get")
    def test_create_post_valid_author(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        url = reverse("posts")
        data = {
            "title": "First Post",
            "content": "This is my first post",
            "author_id": 1
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)