import pytest
from django.core.exceptions import ValidationError
from users.enums import PasswordValidationErrors


def assert_password_common(validator, password):
    """Helper function to assert that a password is considered too common"""
    with pytest.raises(ValidationError) as exc_info:
        validator.validate(password)
    assert str(exc_info.value.messages[0]) == str(PasswordValidationErrors.TOO_COMMON.value)

def assert_password_valid(validator, password):
    """Helper function to assert that a password is valid"""
    validator.validate(password) 