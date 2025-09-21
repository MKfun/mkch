from django import forms
from django.template.loader import render_to_string
from django.http import HttpResponse

class PasscodeEnterForm(forms.Form):
    passcode = forms.CharField(label="Введите пасскод")

class PasscodeGenerateForm(forms.Form):
    pass # пиздец

def render_form(
    request, template_name, context=None, content_type=None, status=None, using=None
):
    """
    Костылирует HttpResponse, заменяя в строке value на placeholder.
    Чуть изменённый django.shortcuts.render().
    """
    content = render_to_string(
        template_name, 
        context, 
        request, 
        using=using
    ).replace("value", "placeholder")
    return HttpResponse(content, content_type, status)