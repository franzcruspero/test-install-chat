import pytest
from users.validators import CommonPasswordValidator


@pytest.fixture
def password_validator():
    return CommonPasswordValidator() 