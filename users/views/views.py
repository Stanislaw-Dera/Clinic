from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from users.models import User, Doctor, Patient
from users.utils import register_with_act_code


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

@login_required(redirect_field_name=None)
def user_profile(request):
    if request.user.role == 'd':
        doc = Doctor.objects.get(user=request.user)

        if request.method == 'POST':
            print("post", request.POST.get('bio'), "files", request.FILES)
            if request.POST.get('bio'):
                doc.bio = request.POST.get('bio')
                doc.save()

                return JsonResponse({'message': 'bio updated successfully'})

            if request.FILES.get('profile_picture'):
                doc.profile_picture = request.FILES['profile_picture']
                doc.save()

                # some photo validation?

        return render(request, 'users/functional/doctor-profile-doc-view.html', {
            "doctor": doc.serialize()
        })

    elif request.user.role == 'p':
        patient = Patient.objects.get(user=request.user)

        try:
            if request.method == 'POST':
                print("post", request.POST)

                if request.POST.get('email'):
                    patient.user.email = request.POST.get('email')
                    patient.user.save()
                if request.POST.get('phone_number'):
                    patient.phone_number = request.POST.get('phone_number')
                if request.POST.get('address'):
                    patient.address = request.POST.get('address')
                if request.POST.get('extra_info'):
                    patient.extra_information = request.POST.get('extra_info')

                patient.save()
                return JsonResponse({'message': 'data updated successfully'})
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

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