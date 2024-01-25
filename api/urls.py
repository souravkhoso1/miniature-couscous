from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home),
    path("generate_token/", views.generate_token),
    path("revoke_token/", views.revoke_token),
]
