import hashlib
import time

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from django.urls import reverse

from .models import Passcode

from boards.models_tools import get_or_create_anon
from boards.models import Anon

from .mixins import StaffMemberRequiredMixin

from .forms import PasscodeEnterForm, PasscodeGenerateForm

def index(request):
    return render(request, 'passcode_index.html')

def passcode_enter(request):
    if request.method == 'POST':
        anon = get_or_create_anon(request)

        form = PasscodeEnterForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            code = hashlib.sha256(data['passcode'].encode("utf-8")).hexdigest()

            v, m = Passcode.objects.validate(hash_code=code)
            if v:
                request.session['passcode'] = code
                anon.passcodes.add(m)
                anon.save()
            else:
                return render(request, 'error.html', {'error': 'Пасскод не найден.'})

            return HttpResponseRedirect('/')
    else:
        form = PasscodeEnterForm(initial={'passcode': 'Пасскод'})
        return render(request, 'basic_form.html', {'form': form})

def passcode_reset(request):
    if 'passcode' in request.session:
        del request.session['passcode']
        return render(request, 'passcode_reset.html')
    else:
        return HttpResponseRedirect(reverse('passcode_enter_form'))

@staff_member_required
def passcode_generate(request):
    if request.method == "POST":
        code = hashlib.sha256(str(time.time()).encode("utf-8")).hexdigest()
        c = Passcode(code=code)
        c.save()
        return render(request, "success_generation.html", {'passcode': code})
    else:
        return render(request, "basic_form.html", {'form': PasscodeGenerateForm(), 'button_text': 'Сгенерировать'})

class PasscodeListView(StaffMemberRequiredMixin, generic.ListView):
    model = Passcode

class PasscodeDetailView(StaffMemberRequiredMixin, generic.DetailView):
    model = Passcode
