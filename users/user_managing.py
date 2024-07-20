from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not name:
            raise ValueError('Users must have a first name')
        if not surname:
            raise ValueError('Users must have a last name')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            surname=surname,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None):
        user = self.create_user(
            email,
            name=name,
            surname=surname,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


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
        # messages.add_message(request, messages.INFO, "Passwords are not the same")
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