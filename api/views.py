from django.http import HttpResponse
from django.shortcuts import render, redirect
import os
from dotenv import load_dotenv
from django.conf import settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from website.models import ShortUrl, HitCount
import json
import random
import string
from django.conf import settings


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

    dotenv_path = os.path.join(settings.BASE_DIR, ".env")
    load_dotenv(dotenv_path)

    api_token = None
    api_token_returned = Token.objects.filter(user=request.user)
    if api_token_returned.count() == 1:
        api_token = api_token_returned[0]

    return render(
        request,
        "api.html",
        {
            "alert_entry": alert_entry,
            "title": "API | Short URL",
            "base_url": os.getenv("BASE_URL"),
            "api_token": api_token,
        },
    )


def generate_token(request):
    if not validate_user_authenticated(request):
        return redirect("/")
    token = Token.objects.create(user=request.user)
    return redirect("/api")


def revoke_token(request):
    if not validate_user_authenticated(request):
        return redirect("/")
    token = Token.objects.get(user=request.user)
    token.delete()
    return redirect("/api")


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def shorten(request):
    input_data = request.data
    short_slug = None
    if "slug" in input_data and len(input_data["slug"]) > 0:
        short_slug = input_data["slug"]
        if ShortUrl.objects.filter(short_slug=short_slug).count() != 0:
            short_slug = None
    if short_slug is None:
        while True:
            short_slug = "".join(
                random.choice(string.ascii_lowercase + string.digits) for _ in range(10)
            )
            if ShortUrl.objects.filter(short_slug=short_slug).count() == 0:
                break
    original_url = input_data["url"]
    loggedin_user = request.user

    short_url_entry = ShortUrl(
        short_slug=short_slug, actual_url=original_url, creator_user=loggedin_user
    )
    short_url_entry.save()

    hit_count_entry = HitCount(short_url=short_url_entry, hit_count=0)
    hit_count_entry.save()

    dotenv_path = os.path.join(settings.BASE_DIR, ".env")
    load_dotenv(dotenv_path)

    return Response(
        {"short_url": os.getenv("BASE_URL") + "/" + short_url_entry.short_slug},
        status=status.HTTP_200_OK,
    )


def validate_user_authenticated(request):
    if not request.user.is_authenticated:
        request.session["set_alert"] = "true"
        request.session["alert_type"] = "alert-danger"
        request.session["alert_message"] = "You're not logged in. Please login first."
        return False
    return True


def validate_request_post_method(request):
    if request.method != "POST":
        request.session["set_alert"] = "true"
        request.session["alert_type"] = "alert-danger"
        request.session["alert_message"] = "Something went wrong. Please try again."
        return False
    return True
