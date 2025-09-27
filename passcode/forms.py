from django import forms

class PasscodeEnterForm(forms.Form):
    passcode = forms.CharField(
        label="Введите пасскод",
        widget=forms.TextInput(attrs={"placeholder": "Пасскод"})
    )

class PasscodeGenerateForm(forms.Form):
    pass # пиздец
