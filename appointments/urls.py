from django.urls import path

from appointments import views

urlpatterns = [
    path('history/', views.patient_history, name='patient_history'),
    path('get-booking-data/<int:doc_id>', views.get_doc_booking_data, name='get_doc_appointments'),
    path('manage/<int:user_id>', views.manage_appointment, name='manage_appointment'),
]