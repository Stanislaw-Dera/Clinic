from django.urls import path

from appointments import views

urlpatterns = [
    path('history/', views.patient_history, name='patient_history'),
]