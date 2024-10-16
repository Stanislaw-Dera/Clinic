import re
import uuid
from datetime import date

from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractBaseUser


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
        # user.is_active = True

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


class DocManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role='d')


class PatientManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role='p')


email_exp = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'


def check_email(email):
    return True if re.fullmatch(email_exp, email) else False


phone_num_exp = r'\+[0-9\s]+'


def check_phone_number(phone_number):
    return True if re.fullmatch(phone_num_exp, str(phone_number)) else False


class User(AbstractBaseUser):
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    email = models.EmailField(max_length=100, unique=True)
    is_active = models.BooleanField(default=False)
    activation_code = models.CharField(max_length=10, blank=True, null=True, unique=True)

    ROLE_CHOICES = [
        ('p', 'Patient'),
        ('d', 'Doctor'),
    ]

    # perm fields
    is_admin = models.BooleanField(default=False)
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, default='p', blank=True)

    objects = CustomUserManager()
    doctors = DocManager()
    patients = PatientManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    def clean(self):
        if not check_email(self.email):
            raise ValidationError('Email is not valid')

    def save(self, *args, **kwargs):
        if not self.activation_code:
            self.activation_code = str(uuid.uuid4())[:10]

        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_staff(self):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def has_perm(self, perm, obj=None):
        return True

    def get_full_name(self):
        return f"{self.name} {self.surname}"

    def is_patient(self):
        return self.role == 'p'

    def is_doctor(self):
        return self.role == 'd'

    def __str__(self):
        return f'{self.name} {self.surname} ({self.id})'


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    blood_group = models.CharField(max_length=3)
    allergies_and_chronic_diseases = models.TextField(blank=True, null=True)
    extra_information = models.TextField(blank=True, null=True)

    def serialize(self):
        return {
            'full_name': self.user.get_full_name(),
            'phone_number': self.phone_number,
            'email': self.user.email,
            'address': self.address,
            'extra_information': self.extra_information,
            'date_of_birth': self.date_of_birth,
            'blood_group': self.blood_group,
            'allergies_and_chronic': self.allergies_and_chronic_diseases
        }

    def __str__(self):
        return f'{self.user.name} {self.user.surname} ({self.id})'

    def clean(self):
        if not check_phone_number(self.phone_number):
            raise ValidationError('Invalid phone number')
        # other field are kind of free to the user

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    SPECIALIZATIONS = (
        ("Allergologist", "Allergologist"),
        ("Anesthesiologist", "Anesthesiologist"),
        ("Cardiologist", "Cardiologist"),
        ("Colon and Rectal Surgeon", "Colon and Rectal Surgeon"),
        ("Dermatologist", "Dermatologist"),
        ("Family Physician", "Family Physician"),
        ("General Surgeon", "General Surgeon"),
        ("Medical Geneticist", "Medical Geneticist"),
        ("Internist", "Internist"),
        ("Neurologist", "Neurologist"),
        ("Neurological Surgeon", "Neurological Surgeon"),
        ("Gynecologist", "Gynecologist"),
        ("Ophthalmic Surgeon", "Ophthalmic Surgeon"),
        ("Orthopaedic Surgeon", "Orthopaedic Surgeon"),
        ("Otolaryngologist", "Otolaryngologist"),
        ("Pathologist", "Pathologist"),
        ("Paediatrician", "Paediatrician"),
        ("Psychiatrists", "Psychiatrists"),
        ("Radiologist", "Radiologist"),
        ("Rheumatologist", "Rheumatologist"),
        ("Urologist", "Urologist"),
        ("Vascular Surgeon", "Vascular Surgeon"),
    )

    profile_picture = models.ImageField(upload_to='doc_pictures', null=True, blank=True)

    started_working = models.DateField(blank=True, null=True)
    specializations = models.CharField(choices=SPECIALIZATIONS, max_length=24)
    bio = models.TextField(blank=True, null=True)

    # not json-serializable
    def short_serialize(self):
        experience = date.today() - self.started_working
        return {
            "full_name": self.user.get_full_name(),
            "specializations": self.specializations,
            "experience": experience.days,
            "profile_picture": str(self.profile_picture)
        }

    def serialize(self):
        experience = date.today() - self.started_working
        return {
            "full_name": self.user.get_full_name(),
            "email": self.user.email,
            "specializations": self.specializations,
            "experience": experience.days,
            "started_working": self.started_working,
            "profile_picture": self.profile_picture,
            "bio": self.bio,
            "certification": [c for c in self.certificates.all()],
        }

    def __str__(self):
        return f'{self.user.name} {self.user.surname} ({self.id})'


class Certificate(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='certificates')
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='certificates/')


class WorkBlock(models.Model):
    start = models.TimeField()
    duration = models.IntegerField(default=30)
    work_day = models.ForeignKey("WorkDay", on_delete=models.CASCADE, related_name='workblocks')

    def __str__(self):
        return (f'{self.work_day.doctor.name} {self.work_day.doctor.surname} workblock starting '
                f'at {self.start} ({self.duration})')


class WorkDayManager(models.Manager):
    def filter_by_doc_and_date(self, doc, date):
        try:
            return super().get_queryset().filter(doctor=doc, date=date).get()
        except ObjectDoesNotExist:
            return super().get_queryset().filter(doctor=doc, day=date.weekday()).get()
        except Doctor.DoesNotExist:
            return super().get_queryset().none()


class WorkDay(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    # empty date - routine workday | empty day - specific date
    date = models.DateField(blank=True, null=True)
    day = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(5)])

    objects = models.Manager()
    filters = WorkDayManager()

    def __str__(self):
        if self.date is None:
            return f"{self.doctor.name}{self.doctor.surname}'s routine workday ({self.day})"
        else:
            return f"{self.doctor.name}{self.doctor.surname}'s workday on {self.date}"

# source: https://www.aucmed.edu/about/blog/a-complete-list-of-medical-specialties-and-subspecialties
# Retrived 9.07.2024
