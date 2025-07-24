from django.urls import path
from . import views


urlpatterns = [
    path('genkey/', views.genkey, name="genkey"),
    path('createuser/', views.createuser, name="createuser")
]
