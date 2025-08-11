"""
URL configuration for mkch project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf import settings

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('boards/', include('boards.urls')),
    path('captcha/', include('captcha.urls')),
    path('key/', include('keyauth.urls')),
    path('api/', include('api.urls')),
    path('passcode/', include('passcode.urls')),
    path('', RedirectView.as_view(url='/boards/', permanent=True)),
    path('settings/', settings_view, name="settings")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
