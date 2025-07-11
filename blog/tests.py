import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog_project.settings")
django.setup()

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from .models import Article, Photo


User = get_user_model()


class ArticleViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.client.login(username="testuser", password="pass")
        self.author = User.objects.create_user(username="author", password="pass")

        self.other_user = User.objects.create_user(username="other", password="pass")
        self.article = Article.objects.create(title="Test", content="Content", author=self.author)

    @patch("blog.views.generate_article_content")
    def test_article_create_view_with_prompt_generates_content(self, mock_generate):
        mock_generate.return_value = "Generated AI content"

        url = reverse("article_create")
        data = {
            "title": "Test Title",
            "content": "",  # Має активувати генерацію
            "prompt": "Write an article about AI",
            "images-TOTAL_FORMS": "0",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "5",
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        article = Article.objects.get(title="Test Title")
        self.assertEqual(article.content, "Generated AI content")
        self.assertEqual(article.author, self.user)
        mock_generate.assert_called_once_with("Write an article about AI")

    @patch("blog.views.generate_article_content")
    def test_article_update_view_only_author_can_update(self, mock_generate):
        article = Article.objects.create(title="Old Title", content="Old content", author=self.user)
        url = reverse("article_edit", kwargs={"pk": article.pk})

        data = {
            "title": "New Title",
            "content": "",
            "prompt": "Update with AI",
            "images-TOTAL_FORMS": "0",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "5",
        }
        mock_generate.return_value = "Updated AI content"

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        article.refresh_from_db()
        self.assertEqual(article.title, "New Title")
        self.assertEqual(article.content, "Updated AI content")

        self.client.logout()
        self.client.login(username="other", password="pass")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_non_author_cannot_edit_article(self):
        self.client.login(username="other", password="pass")

        url = reverse("article_edit", kwargs={"pk": self.article.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

        response_post = self.client.post(url, {
            "title": "Changed Title",
            "content": "Changed content",
            "prompt": "",
            "images-TOTAL_FORMS": "0",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "5",
        })
        self.assertEqual(response_post.status_code, 403)
