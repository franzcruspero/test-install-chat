from django_extensions.db.models import TimeStampedModel

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import OPTIONAL
from core.utils import get_upload_path


class ChatRoomQuerySet(models.QuerySet):
    def latest_message(self):
        return self.prefetch_related(
            models.Prefetch(
                "messages",
                queryset=Message.objects.order_by("-created")[:1],
                to_attr="latest_message",
            )
        )


class ChatRoomManager(models.Manager):
    def get_queryset(self):
        return ChatRoomQuerySet(self.model, using=self._db)


class ChatRoom(TimeStampedModel):
    name = models.CharField(
        _("Name"), max_length=255, help_text=_("Chat room name"), **OPTIONAL
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="chat_rooms", verbose_name=_("Users")
    )

    objects = ChatRoomManager()

    def __str__(self):
        if self.name:
            return f"{self.name} ({self.id})"
        return f"Chat Room {self.id}"


class Message(TimeStampedModel):
    class MessageType(models.TextChoices):
        TEXT = "TEXT", _("Text")
        FILE = "FILE", _("File")
        IMAGE = "IMAGE", _("Image")

    class StatusType(models.TextChoices):
        SENT = "SENT", _("Sent")
        DELIVERED = "DELIVERED", _("Delivered")
        READ = "READ", _("Read")

    room = models.ForeignKey(
        ChatRoom,
        verbose_name=_("Room"),
        related_name="messages",
        on_delete=models.CASCADE,
        help_text=_("Chat room"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        related_name="messages",
        on_delete=models.CASCADE,
        help_text=_("User that sent the message"),
    )
    content = models.TextField(_("Content"), blank=True, help_text=_("Message content"))
    message_type = models.CharField(
        max_length=50,
        choices=MessageType.choices,
        default=MessageType.TEXT,
        help_text=_("Type of message"),
    )
    file = models.FileField(_("File"), upload_to=get_upload_path, **OPTIONAL)
    status = models.CharField(
        _("Status"),
        choices=StatusType.choices,
        default=StatusType.SENT,
        help_text=_("Status of the message"),
        max_length=50,
    )
    parent = models.ForeignKey(
        "self",
        **OPTIONAL,
        related_name="replies",
        on_delete=models.CASCADE,
        help_text=_("Parent message if a user is replying to a specific message"),
    )

    def __str__(self):
        return f"{self.user.email}: {self.content or self.file_url or self.image_url}"
