import hashlib

from functools import wraps
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings

# Update 4.1:
# Now auth_key COOKIES can be used to pass key to the server.
# Update had been made because of thread API hardening.

def key_required(function):
  @wraps(function)
  def wrap(request, *args, **kwargs):
        key = request.COOKIES.get('auth_key', None) or request.session.get('auth_key', None)
        if not key:
            return HttpResponseRedirect(reverse('key_enter_form'))
        key = request.session["auth_key"]

        if key == hashlib.sha256(settings.AUTH_KEY.encode("utf-8")).hexdigest():
            return function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('key_enter_form'))

  return wrap

class KeyRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        key = request.COOKIES.get('auth_key', None) or request.session.get('auth_key', None)
        if not key:
            return HttpResponseRedirect(reverse('key_enter_form'))

        if key == hashlib.sha256(settings.AUTH_KEY.encode("utf-8")).hexdigest():
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied
