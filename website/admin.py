from django.contrib import admin
from .models import ShortUrl, HitCount

# Register your models here.
admin.site.register(ShortUrl)
admin.site.register(HitCount)
