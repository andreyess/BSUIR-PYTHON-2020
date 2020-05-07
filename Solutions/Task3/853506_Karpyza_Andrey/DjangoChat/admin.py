from django.contrib import admin
from .models import Post, Comment, Like, News
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
    raw_id_fields = ('author',)
    list_display = ('body', 'author', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated', 'author')


class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created',)
    list_filter = ('created',)


class LikeAdmin(admin.ModelAdmin):
    raw_id_fields = ('author',)
    list_display = ('post', 'author',)


admin.site.register(Comment, CommentAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(News, NewsAdmin)
