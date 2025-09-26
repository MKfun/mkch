from django import forms

class PasscodeEnterForm(forms.Form):
    passcode = forms.CharField(label="Введите пасскод")

class PasscodeGenerateForm(forms.Form):
    pass # пиздец
