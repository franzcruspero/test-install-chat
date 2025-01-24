import pytest
from rest_framework import status

from django.urls import reverse

from chat.api.v1.tests.factories import ChatRoomFactory, MessageFactory, UserFactory


@pytest.mark.django_db
class TestMessageViewSet:
    def test_get_messages(self, authenticated_api_client, user):
        """
        Test various scenarios for fetching messages from a chat room.
        """
        chat_room = ChatRoomFactory()
        chat_room.users.add(user)

        message1 = MessageFactory(
            room=chat_room, user=user, created="2025-01-01T12:00:00Z"
        )
        message2 = MessageFactory(
            room=chat_room, user=user, created="2025-01-01T12:01:00Z"
        )

        url = reverse(
            "v1:chat:messages-list", kwargs={"parent_lookup_room": chat_room.id}
        )

        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        assert response.data["results"][0]["content"] == message2.content
        assert response.data["results"][1]["content"] == message1.content

        message3 = MessageFactory(
            room=chat_room, user=user, created="2025-01-01T11:59:00Z"
        )
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["content"] == message3.content

        for i in range(30):
            MessageFactory(
                room=chat_room, user=user, created=f"2025-01-01T13:{i:02d}:00Z"
            )
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 10
        assert response.data["next"] is not None

    def test_unauthenticated_user(self, api_client):
        """
        Test that an unauthenticated user cannot access messages.
        """
        chat_room = ChatRoomFactory()
        url = reverse(
            "v1:chat:messages-list", kwargs={"parent_lookup_room": chat_room.id}
        )

        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_room_with_no_messages(self, authenticated_api_client, user):
        """
        Test that a chat room with no messages returns an empty result set.
        """
        chat_room = ChatRoomFactory()
        chat_room.users.add(user)

        url = reverse(
            "v1:chat:messages-list", kwargs={"parent_lookup_room": chat_room.id}
        )

        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0

    def test_room_with_messages_from_multiple_users(
        self, authenticated_api_client, user
    ):
        """
        Test that messages from all users in the same room are returned.
        """
        chat_room = ChatRoomFactory()
        chat_room.users.add(user)

        another_user = UserFactory()
        chat_room.users.add(another_user)

        message1 = MessageFactory(room=chat_room, user=user)
        message2 = MessageFactory(room=chat_room, user=another_user)

        url = reverse(
            "v1:chat:messages-list", kwargs={"parent_lookup_room": chat_room.id}
        )

        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        assert response.data["results"][0]["content"] == message2.content
        assert response.data["results"][1]["content"] == message1.content
