from django.contrib import admin
from .models import Post, Comment
# Register your models here.


class PostAdmin(admin.ModelAdmin):
    list_filter = ('status', 'created', 'publish', 'author') # меню справа, фальтрующее данные
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    search_fields = ('title', 'body') # поиск данных по полям title и body
    prepopulated_fields = {'slug': ('title',)} # поле slug заполняется автоматически во время ввода title
    raw_id_fields = ('author',) # позволяет удобно искать юзера для во время создания нового поста
    date_hierarchy = 'publish' # сначала будут отображаться данные с пометкой publish
    ordering = ['status', 'publish']


class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')


admin.site.register(Comment, CommentAdmin)
admin.site.register(Post, PostAdmin)
