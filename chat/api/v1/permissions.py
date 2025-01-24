from rest_framework.permissions import BasePermission

from chat.models import ChatRoom


class CanViewChatRoom(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        chatroom = obj

        if chatroom.users.filter(id=user.id).exists():
            return True

        if user.is_staff or user.has_perm("chat.view_all_chatrooms"):
            return True

        # Deny access by default
        return False


class CanViewMessage(BasePermission):
    def has_permission(self, request, view):
        chatroom_id = view.kwargs.get("parent_lookup_room")
        if chatroom_id:
            return ChatRoom.objects.filter(id=chatroom_id, users=request.user).exists()

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        message = obj

        if message.room.users.filter(id=user.id).exists():
            return True

        if user.is_staff or user.has_perm("chat.view_all_messages"):
            return True

        # Deny access by default
        return False
