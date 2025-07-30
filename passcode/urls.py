from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='passcode_index'),
    path('enter/', views.passcode_enter, name='passcode_enter_form'),
    path('reset/', views.passcode_reset, name='passcode_reset_form'),
    path('generate/', views.passcode_generate, name='passcode_generate_form')
]
