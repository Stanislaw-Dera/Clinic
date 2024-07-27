from django.db import models

from users.models import Patient, Doctor, User

# Create your models here.


class CategoryManager(models.Manager):
    def for_patient(self):
        return super().get_queryset().filter(public='True')

    def for_doctor(self):
        return super().get_queryset().all()


class Category(models.Model):
    name = models.CharField(max_length=32)
    duration = models.PositiveSmallIntegerField()
    public = models.BooleanField(default=False)

    objects = CategoryManager()

    def can_be_chosen_by_patient(self):
        return self.public


class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    status_choices = (
        ('Upcoming', 'Upcoming'),
        ('Canceled', 'Canceled'),
        ('Finished', 'Finished')
    )

    status = models.CharField(choices=status_choices, max_length=10, default='Upcoming')


