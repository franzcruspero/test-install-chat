import datetime

import pytest
from django.http import HttpRequest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from users.api.v1.serializers import CustomRegisterSerializer
from users.models import User


@pytest.mark.django_db
class TestCustomUserDetailSerializer:
    def test_custom_signup(self, api_client):
        """Test that fields are saved correctly during signup"""
        data = {
            "first_name": "John",
            "last_name": "Smith",
            "phone_number": "9156127824",
            "email": "test@example.com",
            "password1": "x8K#mP9$vL2@nQ5",
            "password2": "x8K#mP9$vL2@nQ5",
        }
        data["username"] = "johnsmith"

        serializer = CustomRegisterSerializer(data=data)
        assert serializer.is_valid() is True

        request = HttpRequest()
        request.session = api_client.session
        serializer.save(request=request)

        user = User.objects.last()

        assert user.first_name == data["first_name"]
        assert user.last_name == data["last_name"]
        assert str(user.phone_number.national_number) == data["phone_number"]
        assert user.username == data["username"]
        assert user.email == data["email"]

        assert User.objects.count() == 1

    def test_update_user_birthday(self, authenticated_api_client, user):
        """Test that birthday field can be updated"""
        birthday_date = "1995-05-05"
        url = reverse("v1:user_detail")
        data = {
            "username": "johnsmith",
            "birthday": birthday_date,
        }

        # Obtain JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Include the token in the request headers
        response = authenticated_api_client.put(
            url, data, HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.birthday == datetime.date.fromisoformat(birthday_date)


@pytest.mark.django_db
class TestCustomPasswordChangeSerializer:
    def test_password_change_incorrect_old_password(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse("v1:rest_password_change")

        data = {
            "old_password": "wrong_password",
            "new_password1": "NewPassword123!",
            "new_password2": "NewPassword123!",
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("old_password")[0] == "Incorrect password. Try again."

    def test_password_change_success(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse("v1:rest_password_change")

        data = {
            "old_password": "password",
            "new_password1": "x8K#mP9$vL2@nQ5",
            "new_password2": "x8K#mP9$vL2@nQ5",
        }

        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK

    def test_password_change_incorrect_new_password1(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse("v1:rest_password_change")

        data = {
            "old_password": "password",
            "new_password1": "NewPassword1234!",
            "new_password2": "NewPassword123!",
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("new_password2")[0] == "Passwords do not match."

    def test_password_change_new_password_same_as_old_password(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse("v1:rest_password_change")

        data = {
            "old_password": "password",
            "new_password1": "password",
            "new_password2": "password",
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.data.get("new_password1")[0]
            == "New password cannot be the same as current password."
        )

    def test_password_change_password_length(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse("v1:rest_password_change")

        data = {
            "old_password": "password",
            "new_password1": "test",
            "new_password2": "test",
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("new_password1")[0] == "Must be at least 8 characters."
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("new_password1")[0] == "Must be at least 8 characters."
