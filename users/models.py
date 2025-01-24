from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from users.storages import UniqueFileStorage


class User(AbstractUser):
    phone_number = PhoneNumberField(
        _("Phone Number"),
        null=True,
    )
    birthday = models.DateField(
        _("Birthday"),
        null=True,
        blank=True,
    )
    profile_picture = models.ImageField(
        null=True, blank=True, storage=UniqueFileStorage()
    )

    @property
    def email_verified(self) -> bool:
        return self.emailaddress_set.filter(verified=True).exists()
