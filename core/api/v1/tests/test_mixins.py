import pytest
from rest_framework_simplejwt.tokens import RefreshToken
from core.api.v1.mixins import TokenResponseMixin
from users.models import User


@pytest.mark.django_db
def test_get_token_response():
    user = User.objects.create_user(username="testuser", password="testpassword")
    mixin = TokenResponseMixin()
    token_response = mixin.get_token_response(user)

    assert "refresh" in token_response
    assert "access" in token_response
    assert token_response["refresh"] is not None
    assert token_response["access"] is not None
    assert isinstance(token_response["refresh"], str)
    assert isinstance(token_response["access"], str)
