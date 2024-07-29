from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from users.models import User
from users.utils import register_with_act_code


# Create your views here.

def index(request):
    return render(request, "users/welcome-page.html")

    # return render(request, "welcome-page.html", {"foo": "foo"})

    # dla view dla lekarzy, view dla pacjentów, view dla niezalogowanych, post=log_out


def login_view(request):
    if request.user.is_authenticated:
        messages.add_message(request, messages.INFO, "You are already logged in.")
        return HttpResponseRedirect(reverse('index'))

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        # print("SESSION KEY: ", request.session.session_key)

        try:
            user = User.objects.get(email=email)
            # print(f"Direct query found user: {user}")
        except User.DoesNotExist:
            # print("User does not exist in direct query")
            user = None

        user = authenticate(request, email=email, password=password)

        if user is not None:
            user.backend = 'users.utils.EmailBackend'
            login(request, user)

            # temporary message
            # messages.add_message(request, messages.INFO, "Logged in.")

            # Redirect to a success page.
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.add_message(request, messages.ERROR, "Invalid login. If you have activation code, register")
            return render(request, 'users/login.html')

    return render(request, 'users/login.html')


def register_view(request):
    if request.user.is_authenticated:
        messages.add_message(request, messages.INFO, "You are already logged in.")
        return HttpResponseRedirect(reverse('index'))

    if request.method == "POST":
        email = request.POST.get("email")
        activation_code = request.POST.get("activation_code")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        print("register: ", email, activation_code)

        try:
            register_with_act_code(email, activation_code, password, confirm_password)
            print('reg with act code successful')
        except ValidationError as e:
            for message in e.messages:
                print('register: ', message)
                messages.add_message(request, messages.ERROR, message)

            return render(request, "users/register.html", context={
                'email': email,
                'activation_code': activation_code,
                'password': password,
                'confirm_password': confirm_password
            })

        messages.add_message(request, messages.INFO, "Registered successfully. You can log in now.")
        return HttpResponseRedirect(reverse("index"))

    return render(request, 'users/register.html')


# @login_required(redirect_field_name=None)
def logout_view(request):
    logout(request)

    messages.add_message(request, messages.INFO, "Logged out successfully.")
    return HttpResponseRedirect(reverse("index"))
