from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('login/', views.login),
    path('auth/', views.auth, name='auth'),
    path('logout/', views.logout),
    path('add-new-entry/', views.add_new_entry, name='add_new_entry')
]