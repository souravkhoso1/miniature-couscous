from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('login/', views.login),
    path('auth/', views.auth, name='auth'),
    path('logout/', views.logout),
]