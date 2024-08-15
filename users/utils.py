from datetime import datetime

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from users.models import User

from clinic.settings import CLINIC_OPENING, CLINIC_CLOSURE, WORKBLOCK_DURATION


def register_with_act_code(email, activation_code, password, password_confirmation):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise ValidationError('User does not exist')

    if user.is_active:
        raise ValidationError('User is already registered. ')

    if activation_code != user.activation_code:
        raise ValidationError('Activation code is invalid. ')

    validate_password(password, user)

    if password != password_confirmation:
        raise ValidationError("Passwords are not the same. ")

    user.set_password(password)
    user.is_active = True
    user.save()

    return True


# backend to modify authenticate method (with help of ai :P)


class EmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        print(f"Authenticating user with email: {email}")

        try:
            user = User.objects.get(email=email)
            print(f"Found user: {user}")

        except User.DoesNotExist:
            print("User does not exist")
            return None

        if user.check_password(password):
            print("Password is correct")
            return user

        print("Password is incorrect")
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def is_hour_valid(date):
    today = datetime.now()
    date = date.replace(year=today.year, month=today.month, day=today.day)
    print(date)
    dates = []

    temp = CLINIC_OPENING

    while temp < CLINIC_CLOSURE:
        dates.append(temp)
        temp += WORKBLOCK_DURATION

    print("dates", dates)

    return date in dates
