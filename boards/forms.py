from django.core.validators import FileExtensionValidator
from django.core import validators
from django.conf import settings
from django import forms

from captcha.fields import CaptchaField

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class FileAllowedField(forms.FileField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    default_validators = [FileExtensionValidator(['pdf'])]

class MultipleFileField(FileAllowedField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={"ondrop": "drop_handler(event)", "ondragenter": "dragenter_handler(event)", "ondragleave": "dragleave_handler(event)", "ondragover": "dragover_handler(event)", "accept": ', '.join(settings.VALID_FILETYPES)}))

        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if isinstance(data, (list, tuple)):
            result = [single_file_clean(x, initial) for x in data]
        else:
            result = [single_file_clean(data, initial)]
        return result

# Хуёво реализованы формы, в интернете DRY-решения не нашёл. Если кто знает - кидайте PR

class FileValidationForm(forms.Form):
    files = MultipleFileField(required=False)

    def is_valid(self, request=None):
        if request:
            for f in request.FILES.getlist("files"):
                print(f)
                if not f.name.split(".")[-1] in settings.VALID_FILETYPES:
                    return False

        return super(FileValidationForm, self).is_valid()

class LockDownForm(forms.Form):
    lock = forms.BooleanField()

class NewThreadFormP(FileValidationForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Заголовок'}), min_length=1, max_length=64)
    text = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Текст'}), max_length=16384)
    is_nsfw = forms.BooleanField(label="NSFW?", required=False)

class ThreadCommentFormP(FileValidationForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Текст'}), max_length=16384)
    is_nsfw = forms.BooleanField(label="NSFW?", required=False)

class NewThreadForm(NewThreadFormP):
    captcha = CaptchaField()

class ThreadCommentForm(ThreadCommentFormP):
    captcha = CaptchaField()
