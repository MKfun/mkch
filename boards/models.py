import hashlib
import re
import statistics
import numpy as np

from django.core.validators import FileExtensionValidator
from django.utils.html import escape
from django.db import models

from passcode.models import Passcode
from .tools import anonymous_file_upload_to

class Anon(models.Model):
    ip = models.GenericIPAddressField(unique=True)

    banned = models.BooleanField(default=False)

    passcodes = models.ManyToManyField(Passcode, blank=True)

class Category(models.Model):
    name = models.TextField(help_text="Название Категории")

    def __str__(self):
        return self.name

class Board(models.Model):
    category = models.ForeignKey(Category, null=True, default=None, on_delete=models.CASCADE)

    code = models.CharField(max_length=20, help_text="Код доски (например, b)", primary_key=True)
    description = models.TextField(help_text="Короткое описание доски, которое пользователи видят в списке рядом с ней")
    detail_description = models.TextField(help_text="Подробное описание доски, видно которое пользователи видят в шапке самой доски", null=True)

    banner = models.FileField(help_text="Приветственный баннер", null=True, default=None)

    thread_limit = models.IntegerField(help_text="Количество тредов, при котором старые начнут удаляться, давая место новым (0 для неограниченного количества)", default=1000)
    bump_limit = models.IntegerField(help_text="Бамплимит. При достижении (бамплимит) комментариев в треде он 'утонет' (удалится) (0 для выключения бамплимита)", default=500)
    is_nsfw = models.BooleanField(help_text="Помечает борд как NSFW. Файлы с тредов в NSFW бордах отправляются МКБотом под спойлером, а сама категория помечается красным цветом.", default=False)
    enable_posting = models.BooleanField(help_text="Если False, разрешает постинг в борде только админам (борда всё ещё будет доступна для просмотра из списка)", default=True)
    lockdown = models.BooleanField(help_text="Карантин. В карантинных бордах НЕЛЬЗЯ создавать или бампать треды.", default=False)

    def __str__(self):
        return self.code

    def has_permission(self, anon):
        codes_a = [p.code for p in anon.permissions.all()]
        codes_b = [p.code for p in self.permissions_required.all()]

        for c in codes_b:
            if c not in codes_a:
                return False
        return True

class Thread(models.Model):
    class Meta:
        permissions = [
            ("create_new_threads", "Can create new threads"),
            ("comment_threads", "Can comment threads")
        ]

    creation = models.DateTimeField(help_text="Дата и время создания", auto_now=True)

    author = models.ForeignKey(Anon, help_text="Создатель треда", on_delete=models.CASCADE, null=True)

    board = models.ForeignKey(Board, help_text="Доска треда", on_delete=models.CASCADE, null=True)

    title = models.CharField(max_length=64, help_text="Заголовок", default="None")
    text = models.TextField(help_text="Текст")

    rating = models.IntegerField(default=0, help_text="Рейтинг треда. Он задаётся автоматически, крайне не рекомендуется менять вручную!!!")
    is_nsfw = models.BooleanField(help_text="Является ли тред NSFW (всегда True для комментов на NSFW бордах)", default=False)

    pinned = models.BooleanField(default=False, help_text="Если тред закреплён, он будет отображаться в самом начале списка тредов. Также можно задать из контектного меню треда если вы админ.")

    def formatted(self):
        t = escape(self.text)
        return t.replace('\n', '<br>')
                
    def rating_pp(self):
        l = [x.rating for x in Thread.objects.filter(board=self.board).exclude(id=self.id)]
        if len(l) == 0 and self.rating == 0:
            self.rating += 1
        elif len(l) > 0:
            highest = max(l)
            if self.rating <= highest:
                self.rating += 1

    def __str__(self):
        return str(self.id)

class Comment(models.Model):
    creation = models.DateTimeField(help_text="Дата и время создания", auto_now=True)

    thread = models.ForeignKey(Thread, help_text="Тред, к которому пишется комментарий", on_delete=models.CASCADE, null=True)

    author = models.ForeignKey(Anon, help_text="Создатель треда", on_delete=models.CASCADE, null=True)
    author_code = models.TextField(help_text="Код автора, задаётся автоматически.", null=True, default=None)
    is_nsfw = models.BooleanField(help_text="Является ли коммент NSFW (всегда True для комментов под NSFW тредами)", default=False)

    text = models.TextField(help_text="Текст")

    def formatted(self):
        t = escape(self.text)

        t = re.sub(r'^(&gt;.*)', r'<span class="quote">\1</span>', t, flags=re.MULTILINE)
        t = re.sub(r'&gt;!(.*?)!&lt;', r'<span class="spoiler">\1</span>', t, re.DOTALL)
        t = re.sub(r'~~([\s\S]+?)~~', r'<del>\1</del>', t)

        t = re.sub(r'#(\d+)', r'<div class="reply"><a class="replylnk" href="#comment_\1">#\1</a></div>', t)

        def mkchtlnk_replacer(match):
            try:
                board_code = match.group(1)
                thread_id = match.group(2) 
                Thread.objects.get(board__code=board_code, id=thread_id)
                return f"<a href='/boards/board/{board_code}/thread/{thread_id}'>{board_code}-&gt;{thread_id}</a>"
            except (Board.DoesNotExist, Thread.DoesNotExist, ValueError):
                return match.group(0)

        t = re.sub(r'mkchtlnk:(\w+):(\d+)', mkchtlnk_replacer, t)

        return t.replace('\n', '<br>')

    def replies(self):
        return Comment.objects.filter(thread=self.thread).filter(text__contains="#"+str(self.id))

    def __str__(self):
        return str(self.thread.id) + ", " + str(self.id)

class ThreadFile(models.Model):
    thread = models.ForeignKey(Thread, help_text="Тред, которому принадлежит файл", on_delete=models.CASCADE, null=True)

    ftypes = {
        'photo': ['png', 'jpg', 'jpeg', 'webp', 'gif'],
        'video': ['mp4', 'webm']
    }
    allowed = ['png', 'jpg', 'jpeg', 'webp', 'mp4', 'webm', 'gif']

    file = models.FileField(help_text="Файл", null=True, validators=[FileExtensionValidator(allowed)], upload_to=anonymous_file_upload_to)

    def fclass(self):
        p = self.file.path.split('.')[-1]
        for k, v in self.ftypes.items():
            if p in v:
                return k
        return "document"

    def type(self):
        return self.file.path.split('.')[-1]

class CommentFile(models.Model):
    comment = models.ForeignKey(Comment, help_text="Коммент, которому принадлежит файл", on_delete=models.CASCADE, null=True)

    ftypes = {
        'photo': ['png', 'jpg', 'jpeg', 'webp', 'gif'],
        'video': ['mp4', 'webm']
    }
    allowed = ['png', 'jpg', 'jpeg', 'webp', 'mp4', 'webm', 'gif']

    file = models.FileField(help_text="Файл", null=True, validators=[FileExtensionValidator(allowed)], upload_to=anonymous_file_upload_to)

    def fclass(self):
        p = self.file.path.split('.')[-1]
        for k, v in self.ftypes.items():
            if p in v:
                return k
        return "document"

    def type(self):
        return self.file.path.split('.')[-1]
