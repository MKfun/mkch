from django.contrib import admin
from .models import Board, Thread, Comment, ThreadFile, CommentFile

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('code',)

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'creation')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'creation')

# raskommentiruyte esli hotite imet vozmoshnost cherez adminku dobavlat / udalyat fayli v tredi / commenti

# @admin.register(ThreadFile)
# class ThreadFileAdmin(admin.ModelAdmin):
#     list_display = ('thread', 'file')

# @admin.register(CommentFile)
# class CommentFileAdmin(admin.ModelAdmin):
#     list_display = ('comment', 'file')
