import pytest
from django.http import HttpRequest
from django.urls import reverse
from rest_framework import status
from users.api.v1.serializers import (CustomRegisterSerializer,
                                      PasswordResetSerializer)
from users.enums import PasswordValidationErrors
from users.forms import AllAuthPasswordResetForm
from users.models import User


class TestPasswordResetSerializer:
    def test_password_reset_form_class(self):
        serializer = PasswordResetSerializer()
        assert serializer.password_reset_form_class == AllAuthPasswordResetForm


@pytest.mark.django_db
class TestCustomRegisterSerializer:
    def test_custom_signup_saves_custom_fields(self, api_client):
        """Test that phone number, first name, and last name fields are saved correctly"""
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

        assert User.objects.count() == 1

        user = User.objects.last()

        assert user.username == data.get("username")
        assert str(user.phone_number.national_number) == data.get("phone_number")
        assert str(user.first_name) == data.get("first_name")
        assert str(user.last_name) == data.get("last_name")


@pytest.mark.django_db
class TestPasswordChangeValidation:
    @pytest.mark.parametrize("test_input,expected_status,expected_error", [
        ('Tr0ub4dor&3', status.HTTP_200_OK, None),
        ('x8K#mP9$vL2@nQ5', status.HTTP_200_OK, None),
        ('password123', status.HTTP_400_BAD_REQUEST, PasswordValidationErrors.TOO_COMMON.value),
        ('admin123!', status.HTTP_400_BAD_REQUEST, PasswordValidationErrors.TOO_COMMON.value),
    ])
    def test_password_change(self, authenticated_api_client, test_input, expected_status, expected_error):
        url = reverse("v1:rest_password_change")
        data = {
            "old_password": "password",
            "new_password1": test_input,
            "new_password2": test_input,
        }
        
        response = authenticated_api_client.post(url, data)
        assert response.status_code == expected_status
        if expected_error:
            assert str(expected_error) in str(response.data)
    def test_validate_old_password_with_social_user(self, api_client, user):
        user.has_usable_password = False
        user.save()
        api_client.force_authenticate(user=user)

        url = reverse("v1:rest_password_change")

        data = {
            "new_password1": "x8K#mP9$vL2@nQ5",
            "new_password2": "x8K#mP9$vL2@nQ5",
        }

        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK