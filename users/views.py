from calendar import HTMLCalendar

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from users.models import User, Doctor, Patient, WorkDay
from users.utils import register_with_act_code
from users.FullHTMLCalendar import FullHTMLCalendar


# Create your views here.

# Logging in and index views

def index(request):
    return render(request, "users/welcome-page/welcome-page.html")


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
            return render(request, 'users/welcome-page/login.html')

    return render(request, 'users/welcome-page/login.html')


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

            return render(request, "users/welcome-page/register.html", context={
                'email': email,
                'activation_code': activation_code,
                'password': password,
                'confirm_password': confirm_password
            })

        messages.add_message(request, messages.INFO, "Registered successfully. You can log in now.")
        return HttpResponseRedirect(reverse("index"))

    return render(request, 'users/welcome-page/register.html')


# @login_required(redirect_field_name=None)
def logout_view(request):
    logout(request)

    messages.add_message(request, messages.INFO, "Logged out successfully.")
    return HttpResponseRedirect(reverse("index"))


# other views

def user_profile(request):
    if request.user.role == 'd':
        doc = Doctor.objects.get(user=request.user)
        profile_picture = doc.profile_picture
        return render(request, 'users/functional/doctor-profile-doc-view.html', {
            "doctor": doc.serialize()
        })

    elif request.user.role == 'p':
        patient = Patient.objects.get(user=request.user)
        return render(request, 'users/functional/patient-profile.html', {
            "patient": patient.serialize()
        })


def doc_profile(request, pk):
    user = User.doctors.get(pk=pk)
    doc = Doctor.objects.get(user=user)

    pass  # w templacie dodaj że jeżeli jesteś doktorem mie ma przycisku view schedule


def patient_profile(request, pk):
    if request.user.role == 'p':
        return HttpResponseRedirect(reverse('user_profile'))

    pass  # doc view wraz z js'em do brania kalendarza z api


# calendars api
def default_calendar(request):
    doc_id = request.GET.get('doc-id')
    month = request.GET.get('month')
    year = request.GET.get('year')

    user = User.doctors.get(pk=doc_id)

    doc = Doctor.objects.get(user=user)

    default_workdays = WorkDay.objects.filter(doctor=doc, date=None)

    workdays_numeric_list = []

    for workday in default_workdays:
        workdays_numeric_list.append(workday.day)

    custom_workdays = WorkDay.objects.filter(date__month=month, date__year=year, doctor=doc)
    custom_days_data = {"free": [], "working": []}

    for workday in custom_workdays:

        custom_days_data["free"].append(workday.date.day) if workday.workblocks.all().count() == 0 \
            else custom_days_data["working"].append(workday.date.day)

    print(custom_days_data)
    calendar = FullHTMLCalendar(custom_days_data)

    for i in range(7):
        calendar.cssclasses[i] = 'cal-day active' if i in workdays_numeric_list else 'cal-day disabled'

    return HttpResponse(calendar.formatmonth(int(year), int(month)))
# czas na frontend!!!