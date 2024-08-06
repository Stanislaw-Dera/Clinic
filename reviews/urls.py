from django.urls import path

from reviews import views

urlpatterns = [
    path('post/', views.post_review, name='post')
]