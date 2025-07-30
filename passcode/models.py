import hashlib
from django.db import models

class PasscodeManager(models.Manager):
    def validate(self, hex_code):
        a = Passcode.objects.all()
        for i in a:
            if i.in_hex() == hex_code:
                return True
        return False

class Passcode(models.Model):
    code = models.TextField(help_text="Ключ")
    objects = PasscodeManager()

    def in_hex(self):
        return hashlib.sha256(self.code.encode("utf-8")).hexdigest()
