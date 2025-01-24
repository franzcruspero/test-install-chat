import pytest

from rest_framework import status

from django.urls import reverse


@pytest.mark.django_db
def test_disconnect_social_account_success(
    authenticated_api_client, user, social_account
):
    url = reverse("v1:social_disconnect")
    response = authenticated_api_client.post(url, {"provider": "google"})
    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Social account disconnected"


@pytest.mark.django_db
def test_disconnect_social_account_not_found(
    authenticated_api_client, user, social_account
):
    url = reverse("v1:social_disconnect")
    response = authenticated_api_client.post(url, {"provider": "facebook"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Social account not found"


@pytest.mark.django_db
def test_disconnect_social_account_no_provider(
    authenticated_api_client, user, social_account
):
    url = reverse("v1:social_disconnect")
    response = authenticated_api_client.post(url, {})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Provider not provided"
