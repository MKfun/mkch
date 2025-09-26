import hashlib
from django.db import models

import boards.models as btools

class PasscodeManager(models.Manager):
    def validate(self, hash_code, request=None):
        a = Passcode.objects.all()
        for i in a:
            if i.in_hash() == hash_code:
                if request:
                    anon = btools.get_or_create_anon(request)
                    anon.passcodes.add(i) # в документации написано что дубликаты не создаются так что кристально похуй
                    anon.save()

                return True, i
        return False, None

    def get_by_hash(self, hash_code):
        a = Passcode.objects.all()
        for i in a:
            if i.in_hash() == hash_code:
                return i
        return None

class Passcode(models.Model):
    code = models.TextField(primary_key=True, help_text="Ключ")
    objects = PasscodeManager()

    def in_hash(self):
        return hashlib.sha256(self.code.encode("utf-8")).hexdigest()
