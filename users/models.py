import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from datetime import date

# Create your models here.

from django.contrib.auth.models import AbstractBaseUser

from users.user_managing import CustomUserManager


class User(AbstractBaseUser):
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    email = models.EmailField(max_length=100, unique=True)
    is_active = models.BooleanField(default=False)
    activation_code = models.CharField(max_length=10, blank=True, null=True, unique=True)

    def __str__(self):
        return f'{self.name} {self.surname} ({self.id})'

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'

    def save(self, *args, **kwargs):
        if not self.activation_code:
            self.activation_code = str(uuid.uuid4())[:10]
        super().save(*args, **kwargs)


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    blood_group = models.CharField(max_length=3)
    allergies_and_chronic_diseases = models.TextField(blank=True, null=True)
    extra_information = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.name} {self.user.surname} ({self.id})'


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

    started_working = models.DateField(blank=True, null=True)
    specializations = models.CharField(choices=SPECIALIZATIONS, max_length=24)

    def __str__(self):
        return f'{self.user.name} {self.user.surname} ({self.id})'


class WorkBlock(models.Model):
    start = models.TimeField()
    duration = models.IntegerField(default=30)
    work_day = models.ForeignKey("WorkDay", on_delete=models.CASCADE)

    def __str__(self):
        return (f'{self.work_day.doctor.user.name} {self.work_day.doctor.user.surname} workblock starting '
                f'at {self.start} ({self.duration})')


class WorkDay(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField(blank=True, null=True)
    day = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(6)])

    def __str__(self):
        if self.date is None:
            return f"{self.doctor.user.name}{self.doctor.user.surname}'s routine workday ({self.day})"
        else:
            return f"{self.doctor.user.name}{self.doctor.user.surname}'s workday on {self.date}"

# source: https://www.aucmed.edu/about/blog/a-complete-list-of-medical-specialties-and-subspecialties
# Retrived 9.07.2024