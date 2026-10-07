from django.contrib import admin
from .models import Conversation, Message
# Register your models here.


class AdminConversation(admin.ModelAdmin):
    list_display = ('user', 'order', 'created_at',)

class AdminMessage(admin.ModelAdmin):
    list_display = ('conversation', 'role', 'content', 'created_at')

admin.site.register(Conversation, AdminConversation)
admin.site.register(Message, AdminMessage)