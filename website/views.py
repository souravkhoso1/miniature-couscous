from pprint import pprint
import json
from django.urls import reverse
from django.shortcuts import render, redirect
from authlib.integrations.django_client import OAuth
from django.contrib.auth.models import User
from django.contrib.auth import login as login_d, logout as logout_d


CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)


def home(request):
    # user = request.session.get('user')
    # if user:
    #     user = json.dumps(user)
    return render(request, 'home.html')


def login(request):
    redirect_uri = request.build_absolute_uri(reverse('auth'))
    return oauth.google.authorize_redirect(request, redirect_uri)


def auth(request):
    token = oauth.google.authorize_access_token(request)
    pprint(token)
    if User.objects.filter(username=token['userinfo']['email']).count() != 1:
        new_user = User.objects.create_user(
            username=token['userinfo']['email'],
            email=token['userinfo']['email'],
            first_name=token['userinfo']['given_name'],
            last_name=token['userinfo']['family_name']
        )
        new_user.save()
        login_d(request, new_user)
        print("New user logged in : " + str(token['userinfo']))
    else:
        existing_user = User.objects.get(username=token['userinfo']['email'])
        login_d(request, existing_user)
        print("User already exists : " + str(token['userinfo']))

    #request.session['user'] = token['userinfo']
    return redirect('/')


def logout (request):
    logout_d(request)
    return redirect('/')
