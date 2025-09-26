from django.urls import path

from .views import *

urlpatterns = [
    path('register', register_webpush, name='regist_v'),
    path('test', pilik_pilik, name="test_v"),
    path('', home, name="push_home")
]
