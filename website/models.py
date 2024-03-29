from django.db import models
from django.contrib.auth.models import User


class ShortUrl(models.Model):
    short_slug = models.CharField(max_length=10)
    actual_url = models.CharField(max_length=1000)
    creator_user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.short_slug


class HitCount(models.Model):
    short_url = models.ForeignKey(ShortUrl, on_delete=models.CASCADE)
    hit_count = models.PositiveIntegerField()

    def __str__(self):
        return self.short_url.short_slug
