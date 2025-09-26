from django import forms

class KeyEnterForm(forms.Form):
    key = forms.CharField(label="Введите ключ", max_length=64)
