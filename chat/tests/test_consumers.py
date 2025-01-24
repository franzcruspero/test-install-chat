import pytest
from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator

from chat.consumers import ChatConsumer
from chat.models import ChatRoom, Message
from users.tests.factories import UserFactory


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestChatConsumer:
    async def test_connection_authenticated_user(self):
        """
        Test that an authenticated user can connect.
        """
        user = await sync_to_async(UserFactory.create)()

        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/?recipient_id={user.id}",
        )
        communicator.scope["user"] = user

        connected, _ = await communicator.connect()
        assert connected

        assert communicator.scope["user"] == user

        await communicator.disconnect()

    async def test_connection_unauthenticated_user(self):
        """
        Test that an unauthenticated user is rejected.
        """
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), "/ws/chat/")
        communicator.scope["user"] = None

        connected, _ = await communicator.connect()
        assert not connected

        await communicator.disconnect()

    async def test_message_sending(self):
        """Test message sending through WebSocket"""
        user = await sync_to_async(UserFactory.create)()
        recipient = await sync_to_async(UserFactory.create)()

        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/?recipient_id={recipient.id}",
        )
        communicator.scope["user"] = user

        connected, _ = await communicator.connect()
        assert connected

        # Send message
        message_data = {
            "content": "Hello, World!",
            "type": "TEXT",
            "parent_id": None,
        }
        await communicator.send_json_to(message_data)

        # Wait for response
        response = await communicator.receive_json_from()
        assert response["message_content"] == "Hello, World!"
        assert response["message_type"] == "TEXT"
        assert response["sender_id"] == user.id

        # Verify message in database
        message = await sync_to_async(Message.objects.get)(
            content="Hello, World!",
            user=user,
        )
        assert message.message_type == "TEXT"

        await communicator.disconnect()

    async def test_group_message_broadcast(self):
        """
        Test that messages are broadcast to all group members.
        """
        user = await sync_to_async(UserFactory.create)()
        room = await sync_to_async(ChatRoom.objects.create)(name="Test Room")
        await sync_to_async(room.users.add)(user)

        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/?recipient_id={user.id}",
        )
        communicator.scope["user"] = user
        communicator.scope["room"] = room

        connected, _ = await communicator.connect()
        assert connected

        # Simulate another user in the room
        other_user = await sync_to_async(UserFactory.create)()
        await sync_to_async(room.users.add)(other_user)

        # Send a message
        await communicator.send_json_to({"content": "Broadcast test", "type": "text"})

        # Receive the broadcasted message
        response = await communicator.receive_json_from()
        assert response["message_content"] == "Broadcast test"

        await communicator.disconnect()
