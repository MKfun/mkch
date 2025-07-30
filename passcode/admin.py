from django.contrib import admin
from .models import *

@admin.register(Passcode)
class PasscodeAdmin(admin.ModelAdmin):
    list_display = ('code',)
