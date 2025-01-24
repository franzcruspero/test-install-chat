from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin

from chat.api.v1.pagination import MessageCursorPagination
from chat.api.v1.permissions import CanViewChatRoom, CanViewMessage
from chat.api.v1.serializers import ChatRoomSerializer, MessageSerializer
from chat.models import ChatRoom, Message


class ChatRoomViewSet(ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated, CanViewChatRoom]
    queryset = ChatRoom.objects.all()
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return (
            ChatRoom.objects.filter(users=self.request.user)
            .order_by("-created")
            .latest_message()
        )


# Use NestedViewSetMixin to automatically filter Messages according to the chatroom
class MessageViewSet(NestedViewSetMixin, ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, CanViewMessage]
    pagination_class = MessageCursorPagination
    queryset = Message.objects.all()
