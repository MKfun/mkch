from django.contrib.auth.models import User
from django.utils.html import escape
from django.db import models

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

    anon = models.BooleanField(help_text="Скрыть имя от отсальных участников (админы всё ещё могут увидеть ник)", default=False)
    author = models.ForeignKey(User, help_text="Создатель треда", on_delete=models.SET_NULL, null=True)

    board = models.ForeignKey(Board, help_text="Доска треда", on_delete=models.SET_NULL, null=True)

    title = models.CharField(max_length=64, help_text="Заголовок", default="None")
    text = models.TextField(help_text="Текст")

    def __str__(self):
        return str(self.id)

    def creation_date(self):
        return str(self.creation)

class Comment(models.Model):
    creation = models.DateTimeField(help_text="Дата и время создания", auto_now=True)

    thread = models.ForeignKey(Thread, help_text="Тред, к которому пишется комментарий", on_delete=models.SET_NULL, null=True)

    anon = models.BooleanField(help_text="Скрыть имя от отсальных участников (админы всё ещё могут увидеть ник)", default=False)
    author = models.ForeignKey(User, help_text="Создатель треда", on_delete=models.SET_NULL, null=True)

    text = models.TextField(help_text="Текст")

    def formatted(self):
        t = escape(self.text) # как же мне похуй
        words = t.split(" ")
        for i, word in enumerate(words):
            if word.startswith("#"):
                word = word[1:]
                words[i] = f"<a href='#comment_{word}'> >> {word}</a>"
        return " ".join(words)

    def __str__(self):
        return str(self.thread.id) + ", " + str(self.id)

    def creation_date(self):
        return str(self.creation)

class ThreadFile(models.Model):
    thread = models.ForeignKey(Thread, help_text="Тред, которому принадлежит файл", on_delete=models.SET_NULL, null=True)
    file = models.FileField(help_text="Файл", null=True)

    ftypes = {
        'photo': ['png', 'jpg', 'jpeg', 'webp'],
        'video': ['mp4', 'webm', 'gif'],
        'document': ['pdf', 'docx']
    }

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
    file = models.FileField(help_text="Файл", null=True)

    ftypes = {
        'photo': ['png', 'jpg', 'jpeg', 'webp'],
        'video': ['mp4', 'webm', 'gif'],
        'document': ['pdf', 'docx']
    }

    def fclass(self):
        p = self.file.path.split('.')[-1]
        for k, v in self.ftypes.items():
            if p in v:
                return k
        return "document"

    def type(self):
        return self.file.path.split('.')[-1]
