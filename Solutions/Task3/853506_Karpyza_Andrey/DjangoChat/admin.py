from django.contrib import admin
from .models import Post, Comment, Like, News, Profile, RegistrationMessage
from django.contrib.auth.models import User
from DjangoChat.MessageProcessing import MessageQueue
# Register your models here.


class CommnetsInline(admin.TabularInline):
    model = Comment


class PostAdmin(admin.ModelAdmin):
    list_filter = ('status', 'created', 'publish', 'author') # меню справа, фальтрующее данные
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    search_fields = ('title', 'body') # поиск данных по полям title и body
    prepopulated_fields = {'slug': ('title',)} # поле slug заполняется автоматически во время ввода title
    raw_id_fields = ('author',) # позволяет удобно искать юзера для во время создания нового поста
    date_hierarchy = 'publish' # сначала будут отображаться данные с пометкой publish
    ordering = ['status', 'publish']
    inlines = [CommnetsInline]


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


class UserInline(admin.StackedInline):
    model = User


class MessagesInline(admin.TabularInline):
    model = RegistrationMessage


def send_confirmation(modeladmin,  request,  queryset):
    for profile in queryset:
        if not profile.verified:
            try:
                response = RegistrationMessage.objects.get(profile=profile)
            except Exception:
                msg = RegistrationMessage.objects.create(profile=profile, sended=False)
                MessageQueue.AddMessageInQueue(msg)
send_confirmation.short_description =  "Send confirmation email"


class ProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_display = ('verified', 'user',)
    list_filter = ('verified',)
    inlines = [MessagesInline]
    actions = [send_confirmation]


admin.site.register(Comment, CommentAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(Profile, ProfileAdmin)
