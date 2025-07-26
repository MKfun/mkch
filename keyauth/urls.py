from django.urls import path, re_path
from . import views

urlpatterns = [
    path('auth/', views.key_enter, name='key_enter_form')
]
