import hashlib
import re

from django.core.validators import FileExtensionValidator
from django.utils.html import escape
from django.db import models

from passcode.models import Passcode
from .tools import get_client_ip

class Anon(models.Model):
    ip = models.GenericIPAddressField(primary_key=True)

    code = models.TextField(default="anon")
    banned = models.BooleanField(default=False)

    passcodes = models.ManyToManyField(Passcode)

class Board(models.Model):
    class Meta:
        permissions = [
            ("upload_large_files", "Can upload large files")
        ]

    code = models.CharField(max_length=20, help_text="Код доски (например, b)", primary_key=True)
    description = models.TextField(help_text="Описание доски, которое видят пользователи в её шапке")

    banner = models.FileField(help_text="Приветственный баннер", null=True)

    thread_limit = models.IntegerField(help_text="Количество тредов, при котором старые начнут удаляться, давая место новым (0 для неограниченного количества)", default=1000)

    def __str__(self):
        return self.code

class Thread(models.Model):
    class Meta:
        permissions = [
            ("create_new_threads", "Can create new threads"),
            ("comment_threads", "Can comment threads")
        ]

    creation = models.DateTimeField(help_text="Дата и время создания", auto_now=True)

    author = models.ForeignKey(Anon, help_text="Создатель треда", on_delete=models.SET_NULL, null=True)

    board = models.ForeignKey(Board, help_text="Доска треда", on_delete=models.SET_NULL, null=True)

    title = models.CharField(max_length=64, help_text="Заголовок", default="None")
    text = models.TextField(help_text="Текст")

    def __str__(self):
        return str(self.id)

class Comment(models.Model):
    creation = models.DateTimeField(help_text="Дата и время создания", auto_now=True)

    thread = models.ForeignKey(Thread, help_text="Тред, к которому пишется комментарий", on_delete=models.SET_NULL, null=True)

    author = models.ForeignKey(Anon, help_text="Создатель треда", on_delete=models.SET_NULL, null=True)

    text = models.TextField(help_text="Текст")

    def formatted(self):
        t = escape(self.text) # как же мне похуй
        words = t.split(" ")
        for i, word in enumerate(words):
            if word.startswith("#"):
                word = word[1:]
                words[i] = f"<a href='#comment_{word}'> >> {word}</a>"
        return " ".join(words)

    def replies(self):
        return Comment.objects.filter(thread=self.thread).filter(text__contains="#"+str(self.id))

    def __str__(self):
        return str(self.thread.id) + ", " + str(self.id)

class ThreadFile(models.Model):
    thread = models.ForeignKey(Thread, help_text="Тред, которому принадлежит файл", on_delete=models.SET_NULL, null=True)

    ftypes = {
        'photo': ['png', 'jpg', 'jpeg', 'webp'],
        'video': ['mp4', 'webm', 'gif']
    }
    allowed = ['png', 'jpg', 'jpeg', 'webp', 'mp4', 'webm', 'gif']

    file = models.FileField(help_text="Файл", null=True, validators=[FileExtensionValidator(allowed)])

    def fclass(self):
        p = self.file.path.split('.')[-1]
        for k, v in self.ftypes.items():
            if p in v:
                return k
        return "document"

    def type(self):
        return self.file.path.split('.')[-1]

class CommentFile(models.Model):
    comment = models.ForeignKey(Comment, help_text="Коммент, которому принадлежит файл", on_delete=models.SET_NULL, null=True)

    ftypes = {
        'photo': ['png', 'jpg', 'jpeg', 'webp'],
        'video': ['mp4', 'webm', 'gif']
    }
    allowed = ['png', 'jpg', 'jpeg', 'webp', 'mp4', 'webm', 'gif']

    file = models.FileField(help_text="Файл", null=True, validators=[FileExtensionValidator(allowed)])

    def fclass(self):
        p = self.file.path.split('.')[-1]
        for k, v in self.ftypes.items():
            if p in v:
                return k
        return "document"

    def type(self):
        return self.file.path.split('.')[-1]

def get_or_create_anon(request):
    ip = get_client_ip(request)
    anon, _ = Anon.objects.get_or_create(ip=ip, defaults={'ip': ip, 'code': re.sub(r'([^0-9]+?)', '', hashlib.sha256(ip.encode("utf-8")).hexdigest())[:6], 'banned': False})
    return anon
