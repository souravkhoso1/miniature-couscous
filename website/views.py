from pprint import pprint
import json

from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import render, redirect
from authlib.integrations.django_client import OAuth
from django.contrib.auth.models import User
from django.contrib.auth import login as login_d, logout as logout_d
from .models import ShortUrl

CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"
oauth = OAuth()
oauth.register(
    name="google",
    server_metadata_url=CONF_URL,
    client_kwargs={"scope": "openid email profile"},
)


def home(request):
    if "set_alert" in request.session:
        alert_type = request.session["alert_type"]
        alert_message = request.session["alert_message"]
        alert_entry = {"alert_type": alert_type, "alert_message": alert_message}
        try:
            del request.session["set_alert"]
        except KeyError:
            pass
        try:
            del request.session["alert_type"]
        except KeyError:
            pass
        try:
            del request.session["alert_message"]
        except KeyError:
            pass
    else:
        alert_entry = None

    if request.user.is_authenticated:
        short_urls = ShortUrl.objects.filter(creator_user=request.user)
    else:
        short_urls = None

    return render(
        request, "home.html", {"alert_entry": alert_entry, "short_urls": short_urls}
    )


def login(request):
    redirect_uri = request.build_absolute_uri(reverse("auth"))
    return oauth.google.authorize_redirect(request, redirect_uri)


def auth(request):
    token = oauth.google.authorize_access_token(request)
    pprint(token)
    if User.objects.filter(username=token["userinfo"]["email"]).count() != 1:
        new_user = User.objects.create_user(
            username=token["userinfo"]["email"],
            email=token["userinfo"]["email"],
            first_name=token["userinfo"]["given_name"],
            last_name=token["userinfo"]["family_name"],
        )
        new_user.save()
        login_d(request, new_user)
        print("New user logged in : " + str(token["userinfo"]))
    else:
        existing_user = User.objects.get(username=token["userinfo"]["email"])
        login_d(request, existing_user)
        print("User already exists : " + str(token["userinfo"]))

    return redirect("/")


def logout(request):
    logout_d(request)
    return redirect("/")


def add_new_entry(request):
    if not request.user.is_authenticated:
        request.session["set_alert"] = "true"
        request.session["alert_type"] = "alert-danger"
        request.session["alert_message"] = "You're not logged in. Please login first."
        return redirect("/")
    elif request.method != "POST":
        request.session["set_alert"] = "true"
        request.session["alert_type"] = "alert-danger"
        request.session["alert_message"] = "Something went wrong. Please try again."
        return redirect("/")
    else:
        # TODO: Generate random slug if user has not provided
        short_slug = request.POST.get("shortSlug")
        original_url = request.POST.get("originalUrl")
        loggedin_user = request.user

        short_url_entry = ShortUrl(
            short_slug=short_slug, actual_url=original_url, creator_user=loggedin_user
        )

        short_url_entry.save()
        request.session["set_alert"] = "true"
        request.session["alert_type"] = "alert-success"
        request.session["alert_message"] = "Short URL saved successfully."
        return redirect("/")


def update_entry(request, short_url_id):
    if not request.user.is_authenticated:
        request.session["set_alert"] = "true"
        request.session["alert_type"] = "alert-danger"
        request.session["alert_message"] = "You're not logged in. Please login first."
        return redirect("/")
    elif request.method != "POST":
        request.session["set_alert"] = "true"
        request.session["alert_type"] = "alert-danger"
        request.session["alert_message"] = "Something went wrong. Please try again."
        return redirect("/")
    else:
        short_url_entry = ShortUrl.objects.filter(
            id=short_url_id, creator_user=request.user
        )
        if short_url_entry.count() != 1:
            request.session["set_alert"] = "true"
            request.session["alert_type"] = "alert-danger"
            request.session["alert_message"] = "Invalid request. Please try again."
            return redirect("/")
        else:
            short_url_entry = ShortUrl.objects.get(
                id=short_url_id, creator_user=request.user
            )

            short_slug = request.POST.get("shortSlug")
            original_url = request.POST.get("originalUrl")
            short_url_entry.short_slug = short_slug
            short_url_entry.actual_url = original_url

            short_url_entry.save()
            request.session["set_alert"] = "true"
            request.session["alert_type"] = "alert-success"
            request.session["alert_message"] = "Short URL updated successfully."
            return redirect("/")


def delete_entry(request, short_url_id):
    if not request.user.is_authenticated:
        request.session["set_alert"] = "true"
        request.session["alert_type"] = "alert-danger"
        request.session["alert_message"] = "You're not logged in. Please login first."
        return redirect("/")
    elif request.method != "POST":
        request.session["set_alert"] = "true"
        request.session["alert_type"] = "alert-danger"
        request.session["alert_message"] = "Something went wrong. Please try again."
        return redirect("/")
    else:
        short_url_entry = ShortUrl.objects.filter(
            id=short_url_id, creator_user=request.user
        )
        if short_url_entry.count() != 1:
            request.session["set_alert"] = "true"
            request.session["alert_type"] = "alert-danger"
            request.session["alert_message"] = "Invalid request. Please try again."
            return redirect("/")
        else:
            short_url_entry = ShortUrl.objects.get(
                id=short_url_id, creator_user=request.user
            )
            short_url_entry.delete()

            request.session["set_alert"] = "true"
            request.session["alert_type"] = "alert-success"
            request.session["alert_message"] = "Short URL deleted successfully."
            return redirect("/")


def redirect_to(request, short_url_slug):
    short_url_item = ShortUrl.objects.filter(short_slug=short_url_slug)
    if short_url_item.count() == 1:
        return redirect(ShortUrl.objects.get(short_slug=short_url_slug).actual_url)
    else:
        request.session["set_alert"] = "true"
        request.session["alert_type"] = "alert-danger"
        request.session["alert_message"] = f"Slug '{short_url_slug}' is not available."
        return redirect("/")
