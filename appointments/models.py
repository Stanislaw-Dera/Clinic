from django.db import models

from users.models import User

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

    def __str__(self):
        return self.name


class Appointment(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_appointments')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    date_time = models.DateTimeField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)

    status_choices = (
        ('Upcoming', 'Upcoming'),
        ('Cancelled', 'Cancelled'),
        ('Finished', 'Finished')
    )

    status = models.CharField(choices=status_choices, max_length=10, default='Upcoming')

    def serialize(self):
        return {
            'doctor': self.doctor.get_full_name(),
            'date_time': self.date_time,
            'type': self.category.name,
            'status': self.status,
            'notes': self.notes
        }

    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.doctor.get_full_name()} at {self.date_time}"
