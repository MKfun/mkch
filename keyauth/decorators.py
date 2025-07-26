import hashlib

from functools import wraps
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings

def key_required(function):
  @wraps(function)
  def wrap(request, *args, **kwargs):
        if not 'auth_key' in request.session:
            return HttpResponseRedirect(reverse('key_enter_form'))
        key = request.session["auth_key"]

        if key == hashlib.sha256(settings.AUTH_KEY.encode("utf-8")).hexdigest():
            return function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('key_enter_form'))

  return wrap

class KeyRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not 'auth_key' in request.session:
            return HttpResponseRedirect(reverse('key_enter_form'))
        key = request.session["auth_key"]

        if key == hashlib.sha256(settings.AUTH_KEY.encode("utf-8")).hexdigest():
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied
