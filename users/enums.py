from enum import Enum

from django.utils.translation import gettext_lazy as _


class PasswordValidationErrors(Enum):
    TOO_COMMON = _("This password is too common.")
    HELP_TEXT = _("Your password cannot be a commonly used password.") 