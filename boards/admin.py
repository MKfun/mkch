from django.contrib import admin
from .models import BanReason, BanCase, Board, Thread, Comment, Anon, ThreadFile, CommentFile, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('code', 'lockdown')

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'creation')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'creation')

@admin.register(Anon)
class AnonAdmin(admin.ModelAdmin):
    list_display = ('ip', 'banned')

@admin.register(BanReason)
class BanReasonAdmin(admin.ModelAdmin):
    list_display = ('code', 'description')

@admin.register(BanCase)
class BanReasonAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment')

# раскомментируйте если хотите иметь возможность добавлять / удалять файлы в тредах / комментах в админке (зачастую не нужно)

# @admin.register(ThreadFile)
# class ThreadFileAdmin(admin.ModelAdmin):
#     list_display = ('thread', 'file')

# @admin.register(CommentFile)
# class CommentFileAdmin(admin.ModelAdmin):
#     list_display = ('comment', 'file')
