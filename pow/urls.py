from django.urls import path
from . import views

urlpatterns = [
    path('challenge/', views.get_challenge, name='pow_challenge'),
    path('validate/', views.validate_challenge, name='pow_validate'),
]
