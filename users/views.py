from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, "welcome-page.html")

    # dla view dla lekarzy, view dla pacjentów, view dla niezalogowanych, post=log_out


def login_view(request):
    if request.user.is_authenticated:
        messages.add_message(request, messages.INFO, "You are already logged in.")
        return HttpResponseRedirect('index')

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        print(type(user), user)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return HttpResponseRedirect("index")
        else:
            messages.add_message(request, messages.ERROR, "Invalid login. If you have activation code, register")
            return render(request, 'login.html')

    return render(request, 'login.html')


def register_view(request):
    if request.method == "POST":
        pass

    return render(request, 'register.html')