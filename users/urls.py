from django.urls import path

from users import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('profile/', views.user_profile, name='user_profile'),
    path('doctors/<int:pk>/', views.doc_profile, name='doc_profile'),
    path('patients/<int:pk>/', views.patient_profile, name='doc_profile'),

    path('calendar', views.doctor_calendar, name='calendar'),
    path('get-workhours', views.get_workhours, name='get_workhours'),
    path('change-workblock', views.change_workblock, name='change_workblock'),
]
