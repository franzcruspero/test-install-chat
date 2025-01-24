import factory

from chat.models import ChatRoom, Message
from users.tests.factories import UserFactory


class ChatRoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChatRoom

    name = factory.Faker("word")


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    room = factory.SubFactory(ChatRoomFactory)
    user = factory.SubFactory(UserFactory)
    content = factory.Faker("text")
    message_type = factory.Iterator(
        [Message.MessageType.TEXT, Message.MessageType.FILE, Message.MessageType.IMAGE]
    )
    file = None
    status = factory.Iterator(
        [Message.StatusType.SENT, Message.StatusType.DELIVERED, Message.StatusType.READ]
    )
    parent = None
