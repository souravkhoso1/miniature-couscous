from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('login/', views.login),
    path('auth/', views.auth, name='auth'),
    path('logout/', views.logout),
    path('add-new-entry/', views.add_new_entry, name='add_new_entry'),
    path('update-entry/<int:short_url_id>/', views.update_entry, name='update_entry'),
    path('delete-entry/<int:short_url_id>/', views.delete_entry, name='delete_entry')
]