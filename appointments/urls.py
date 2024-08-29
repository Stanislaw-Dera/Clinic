from django.urls import path

from appointments import views

urlpatterns = [
    path('history', views.patient_history, name='patient_history'),
    path('history-api', views.patient_history_api, name='patient_history_api'),
    path('patient-history/<int:patient_id>', views.patient_history_doc, name='patient_history_for_doc'),
    path('get-booking-data/<int:doc_id>', views.get_doc_booking_data, name='get_doc_appointments'),
    path('manage/<int:user_id>', views.manage_appointment, name='manage_appointment'),
]