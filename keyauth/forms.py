from django import forms

class KeyEnterForm(forms.Form):
    key = forms.CharField(
        label="Введите ключ", 
        widget=forms.TextInput(attrs={"placeholder": "Ключ"}),
        max_length=64)
