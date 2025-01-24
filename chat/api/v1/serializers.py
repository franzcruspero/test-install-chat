from django_restql.fields import DynamicSerializerMethodField
from django_restql.mixins import DynamicFieldsMixin
from rest_framework import serializers

from chat.models import ChatRoom, Message
from users.api.v1.serializers import UserDetailSerializer


class MessageSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "user",
            "content",
            "message_type",
            "file",
            "parent",
        ]


class ChatRoomSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    latest_message = DynamicSerializerMethodField()
    users = UserDetailSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "name",
            "users",
            "latest_message",
        ]

    def get_latest_message(self, obj, parsed_query):
        return (
            MessageSerializer(obj.latest_message[0], parsed_query=parsed_query).data
            if obj.latest_message
            else None
        )
