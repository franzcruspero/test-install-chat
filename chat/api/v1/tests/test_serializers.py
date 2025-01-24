import pytest

from chat.api.v1.serializers import ChatRoomSerializer, MessageSerializer
from chat.api.v1.tests.factories import ChatRoomFactory, MessageFactory, UserFactory
from chat.models import ChatRoom


@pytest.mark.django_db
class TestMessageSerializer:
    def test_serialize_chat_room(self):
        # Create a ChatRoom and associated data
        chat_room = ChatRoomFactory()
        user1 = UserFactory()
        user2 = UserFactory()
        chat_room.users.add(user1, user2)

        # Create a message for the chat room
        message = MessageFactory(room=chat_room)

        # Fetch the chat room using the queryset with latest_message annotation
        chat_room_with_latest_message = (
            ChatRoom.objects.filter(id=chat_room.id).latest_message().first()
        )

        # Serialize the chat room
        serializer = ChatRoomSerializer(chat_room_with_latest_message)

        # Assertions
        assert serializer.data["id"] == chat_room.id
        assert serializer.data["name"] == chat_room.name
        assert len(serializer.data["users"]) == 2
        assert serializer.data["latest_message"] is not None
        assert serializer.data["latest_message"]["id"] == message.id

    def test_serialize_message_with_missing_optional_fields(self):
        message = MessageFactory(file=None, parent=None)
        serializer = MessageSerializer(message)
        assert serializer.data["file"] is None
        assert serializer.data["parent"] is None


@pytest.mark.django_db
class TestChatRoomSerializer:
    def test_serialize_chat_room(self):
        chat_room = ChatRoomFactory()
        user1 = UserFactory()
        user2 = UserFactory()
        chat_room.users.add(user1, user2)

        message = MessageFactory(room=chat_room)

        # Fetch the chat room using the queryset with latest_message annotation
        chat_room_with_latest_message = (
            ChatRoom.objects.filter(id=chat_room.id).latest_message().first()
        )

        serializer = ChatRoomSerializer(chat_room_with_latest_message)

        assert serializer.data["id"] == chat_room.id
        assert serializer.data["name"] == chat_room.name
        assert len(serializer.data["users"]) == 2
        assert serializer.data["latest_message"] is not None
        assert serializer.data["latest_message"]["id"] == message.id

    def test_serialize_chat_room_with_no_messages(self):
        chat_room = ChatRoomFactory()

        # Fetch the chat room using the queryset with latest_message annotation
        chat_room_with_latest_message = (
            ChatRoom.objects.filter(id=chat_room.id).latest_message().first()
        )

        serializer = ChatRoomSerializer(chat_room_with_latest_message)

        assert serializer.data["latest_message"] is None

    def test_serialize_chat_room_with_no_users(self):
        chat_room = ChatRoomFactory()

        # Fetch the chat room using the queryset with latest_message annotation
        chat_room_with_latest_message = (
            ChatRoom.objects.filter(id=chat_room.id).latest_message().first()
        )

        serializer = ChatRoomSerializer(chat_room_with_latest_message)

        assert len(serializer.data["users"]) == 0
