import pytest
from rest_framework.serializers import ValidationError
from allauth.socialaccount.models import SocialAccount


from core.api.v1.serializers import ConstanceSerializer, SocialAccountSerializer


@pytest.mark.django_db
def test_constance_serializer_validation():
    """Test the validation and serialization of valid data."""
    valid_data = {
        "key": "TEST_KEY",
        "value": "mock_value",
    }
    serializer = ConstanceSerializer(data=valid_data)
    assert serializer.is_valid()
    assert serializer.validated_data == valid_data


@pytest.mark.django_db
def test_constance_serializer_invalid_data():
    """Test the validation of invalid data."""
    invalid_data = {
        "key": "",
        "value": "mock_value",
    }
    serializer = ConstanceSerializer(data=invalid_data)

    with pytest.raises(ValidationError):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_social_account_serializer(user, social_account):
    social_account2 = SocialAccount.objects.create(user=user, provider="facebook")
    providers = [social_account.provider, social_account2.provider]
    serializer = SocialAccountSerializer(providers)
    data = serializer.data

    assert "providers" in data
    assert isinstance(data["providers"], list)
    assert social_account.provider in data["providers"]
    assert social_account2.provider in data["providers"]
