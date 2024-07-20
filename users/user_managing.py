from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
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
