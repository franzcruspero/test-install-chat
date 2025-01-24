from unfold.admin import ModelAdmin

from django.contrib import admin

from chat.models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(ModelAdmin):
    list_display = ("id", "name")
    unfold_fields = ("id", "name", "users")
    readonly_fields = ("id",)


@admin.register(Message)
class MessageAdmin(ModelAdmin):
    unfold_fields = (
        "room",
        "user",
        "message_type",
        "timestamp",
        "content",
        "file_url",
        "image_url",
    )
