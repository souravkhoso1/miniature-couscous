from django.urls import path, include
from . import views
from django.views.generic.base import TemplateView
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap

sitemaps = {"static": StaticViewSitemap}

urlpatterns = [
    path("", views.home, name="home"),
    # path("api/", include("api.urls")),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("login/", views.login),
    path("auth/", views.auth, name="auth"),
    path("logout/", views.logout),
    path("add-new-entry/", views.add_new_entry, name="add_new_entry"),
    path("update-entry/<int:short_url_id>/", views.update_entry, name="update_entry"),
    path("delete-entry/<int:short_url_id>/", views.delete_entry, name="delete_entry"),
    path("<str:short_url_slug>/", views.redirect_to, name="redirect_to"),
]
