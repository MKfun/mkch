from django.core import validators
from django import forms

from captcha.fields import CaptchaField

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class AllowedFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    default_validators = [validators.FileExtensionValidator(['png', 'jpg', 'jpeg', 'webp', 'mp4', 'webm', 'gif'])]

class MultipleFileField(AllowedFileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if isinstance(data, (list, tuple)):
            result = [single_file_clean(x, initial) for x in data]
        else:
            result = [single_file_clean(data, initial)]

        return result

# Хуёво реализованы формы, в интернете DRY-решения не нашёл. Если кто знает - кидайте PR

class NewThreadForm(forms.Form):
    title = forms.CharField(min_length=1, max_length=64)
    text = forms.CharField(widget=forms.Textarea, max_length=16384)
    files = MultipleFileField(required=False)
    captcha = CaptchaField()

class ThreadCommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, max_length=16384)
    files = MultipleFileField(required=False)
    captcha = CaptchaField()

class NewThreadFormP(forms.Form):
    title = forms.CharField(min_length=1, max_length=64)
    text = forms.CharField(widget=forms.Textarea, max_length=16384)
    files = MultipleFileField(required=False)

class ThreadCommentFormP(forms.Form):
    text = forms.CharField(widget=forms.Textarea, max_length=16384)
    files = MultipleFileField(required=False)
