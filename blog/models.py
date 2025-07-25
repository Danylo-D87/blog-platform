from django.db import models

from django.conf import settings


class Article(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articles",
    )
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_first_image(self):
        for photo in self.images.all():
            if photo.image:
                return photo
        return None

    class Meta:
        ordering = ["-created_at"]


class Photo(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="article_photos", blank=True)

    def __str__(self):
        return f"Photo for article: {self.article.title}"
