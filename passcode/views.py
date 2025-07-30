import hashlib

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Passcode
from .forms import PasscodeEnterForm

def index(request):
    return render(request, 'passcode_index.html')

def passcode_enter(request):
    if request.method == 'POST':
        form = PasscodeEnterForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            code = hashlib.sha256(data['passcode'].encode("utf-8")).hexdigest()

            if Passcode.objects.validate(hex_code=code):
                request.session['passcode'] = code
            else:
                return render(request, 'error.html', {'error': 'Пасскод не найден.'})

            return HttpResponseRedirect('/')
    else:
        form = PasscodeEnterForm(initial={'passcode': 'Пасскод'})
        return render(request, 'enter_key.html', {'form': form})

def passcode_reset(request):
    if 'passcode' in request.session:
        del request.session['passcode']
        return render(request, 'passcode_reset.html')
    else:
        return HttpResponseRedirect(reverse('passcode_enter_form'))
