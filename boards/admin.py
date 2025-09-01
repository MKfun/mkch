from django.contrib import admin
from .models import Board, Thread, Comment, Anon, ThreadFile, CommentFile, Category, Permission

@admin.register(Permission)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('code', )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('code', 'lockdown')
    filter_horizontal = ('permissions_required', )

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'creation')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'creation')

@admin.register(Anon)
class AnonAdmin(admin.ModelAdmin):
    list_display = ('ip', 'banned')
    filter_horizontal = ('permissions', )

# raskommentiruyte esli hotite imet vozmoshnost cherez adminku dobavlat / udalyat fayli v tredi / commenti

# @admin.register(ThreadFile)
# class ThreadFileAdmin(admin.ModelAdmin):
#     list_display = ('thread', 'file')

# @admin.register(CommentFile)
# class CommentFileAdmin(admin.ModelAdmin):
#     list_display = ('comment', 'file')
