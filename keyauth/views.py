import hashlib

from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseRedirect
from .forms import KeyEnterForm

def key_enter(request):
    if request.method == 'POST':
        form = KeyEnterForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            key = hashlib.sha256(data['key'].encode("utf-8")).hexdigest()

            if key == hashlib.sha256(settings.AUTH_KEY.encode("utf-8")).hexdigest():
                request.session['auth_key'] = key
            else:
                return render(request, 'error.html', {'error': 'Неправильный ключ!'})

            return HttpResponseRedirect('/')
    else:
        form = KeyEnterForm(initial={'key': 'Ключ'})
        return render(request, 'basic_form.html', {'form': form})
