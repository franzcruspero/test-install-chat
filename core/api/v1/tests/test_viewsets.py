import pytest

from constance import config
from constance import settings as constance_settings
from rest_framework import status

from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
def test_constance_viewset(authenticated_api_client, user):
    authenticated_api_client.force_authenticate(user=user)
    url = reverse("v1:core:constance-list")
    response = authenticated_api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    keys = [
        key
        for key in constance_settings.CONFIG.keys()
        if key not in settings.EXCLUDED_KEYS_FOR_API
    ]
    constance_values = [(key, getattr(config, key)) for key in keys]
    assert len(response.data) == len(constance_values)


@pytest.mark.django_db
def test_social_account_viewset(authenticated_api_client, user, social_account):
    authenticated_api_client.force_authenticate(user=user)
    url = reverse("v1:core:social-accounts-list")
    response = authenticated_api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    assert "providers" in response.data[0]
    assert isinstance(response.data[0]["providers"], list)
    assert "google" in response.data[0]["providers"]
