import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        """
        Handle WebSocket connection. Only authenticated users who are part of a valid one-to-one chat can connect.
        """
        user = self.scope["user"]
        recipient = None

        if user and user.is_authenticated:
            # Extract recipient_id from query parameters
            recipient_id = (
                self.scope.get("query_string").decode().split("recipient_id=")[-1]
                if "recipient_id=" in self.scope.get("query_string").decode()
                else None
            )

            # Extract room id from query parameters
            room_id = (
                self.scope.get("query_string").decode().split("room_id=")[-1]
                if "room_id=" in self.scope.get("query_string").decode()
                else None
            )

            # Lazy import of User model
            from django.contrib.auth import get_user_model

            # If theres no room id passed then we verify the recipient_id if they exist
            if room_id is None:
                User = get_user_model()
                try:
                    recipient = await User.objects.aget(id=recipient_id)
                except User.DoesNotExist:
                    await self.close()
                    return
            # Ensure the room exists, create if it doesn't
            self.chat_room = await self.get_or_create_chat_room(
                user, recipient, room_id
            )

            # Use the room's id as the channel layer group name
            self.room_group_name = f"chat_{self.chat_room.id}"

            # Verify user is a participant in the room
            is_member = await sync_to_async(
                self.chat_room.users.filter(id=user.id).exists
            )()
            if is_member:
                # Add user to the channel layer group
                await self.channel_layer.group_add(
                    self.room_group_name, self.channel_name
                )
                await self.accept()
            else:
                await self.close()
        else:
            await self.close()

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        """
        if hasattr(self, "room_group_name") and hasattr(self, "channel_name"):
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

    async def receive_json(self, content):
        """
        Handle incoming WebSocket messages.
        """
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return

        message_content = content.get("content", "")
        message_type = content.get("type", "TEXT")
        parent_id = content.get("parent_id", None)

        # If a parent_id is provided, try to get the parent message
        parent_message = None

        from chat.models import Message

        if parent_id:
            try:
                parent_message = await Message.objects.aget(id=parent_id)
            except Message.DoesNotExist:
                return  # Invalid parent_id, don't send the message

        # Save the message to the database
        await Message.objects.acreate(
            room=self.chat_room,
            user=user,
            content=message_content,
            message_type=message_type,
            parent=parent_message,
        )
        # Broadcast the message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message_type": message_type,
                "message_content": message_content,
                "sender_id": user.id,
                "parent_id": parent_message.id if parent_message else None,
            },
        )

    async def chat_message(self, event):
        """
        Send message to WebSocket client.
        """
        await self.send(
            text_data=json.dumps(
                {
                    "message_type": event["message_type"],
                    "message_content": event["message_content"],
                    "sender_id": event["sender_id"],
                    "parent_id": event["parent_id"],
                }
            )
        )

    async def get_or_create_chat_room(self, user, recipient=None, room_id: str = None):
        """
        Get or create a one-to-one chat room between two users.
        """
        from chat.models import ChatRoom

        if room_id:
            try:
                chat_room = await ChatRoom.objects.aget(id=room_id)
                return chat_room
            except ChatRoom.DoesNotExist:
                return None
        else:
            # Try to find existing room
            chat_room = await ChatRoom.objects.filter(
                users__in=[user, recipient]
            ).afirst()
            if not chat_room:
                # Create new room if doesn't exist
                chat_room = await ChatRoom.objects.acreate()
                await sync_to_async(chat_room.users.add)(user, recipient)

            return chat_room
