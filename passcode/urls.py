from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='passcode_index'),
    path('enter/', views.passcode_enter, name='passcode_enter_form'),
    path('reset/', views.passcode_reset, name='passcode_reset_form'),
    path('generate/', views.passcode_generate, name='passcode_generate_form'),
    path('list/', views.PasscodeListView.as_view()),
    re_path(r'^detail/(?P<pk>\w+)$', views.PasscodeDetailView.as_view())
]
