from datetime import timedelta

import pytest
from allauth.account.models import EmailAddress, EmailConfirmation
from allauth.account.utils import user_pk_to_url_str
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.signing import Signer
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from users.models import User


@pytest.mark.django_db
class TestUserDetailView:
    def test_get_user_detail_success(self, authenticated_api_client, user):
        url = reverse("v1:user_detail")
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == user.username
        assert response.data["email"] == user.email

    def test_update_user_success(self, authenticated_api_client, user):
        url = reverse("v1:user_detail")
        data = {
            "username": "newusername",
            "email": "newemail@example.com",
        }
        response = authenticated_api_client.put(url, data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.username == "newusername"
        assert user.email == "newemail@example.com"

    def test_partial_update_user_success(self, authenticated_api_client, user):
        url = reverse("v1:user_detail")
        data = {
            "first_name": "NewFirstName",
        }
        response = authenticated_api_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == "NewFirstName"

    def test_delete_user_success(self, authenticated_api_client, user):
        url = reverse("v1:user_detail")
        response = authenticated_api_client.delete(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"detail": "A confirmation email has been sent."}


@pytest.mark.django_db
class TestProfilePictureUploadView:
    def test_upload_profile_picture_success(
        self, authenticated_api_client, create_dummy_image
    ):
        url = reverse("v1:profile_picture_upload")
        response = authenticated_api_client.post(
            url, data={"profile_picture": create_dummy_image}
        )

        assert response.status_code == status.HTTP_200_OK
        assert "profile_picture" in response.data
        assert response.data["profile_picture"] is not None

    def test_upload_profile_picture_unauthenticated(
        self, api_client, create_dummy_image
    ):
        url = reverse("v1:profile_picture_upload")
        response = api_client.post(url, data={"profile_picture": create_dummy_image})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_upload_unsupported_image_type(self, authenticated_api_client):
        url = reverse("v1:profile_picture_upload")

        unsupported_file = SimpleUploadedFile(
            "unsupported_file.txt", b"This is not an image.", content_type="text/plain"
        )

        response = authenticated_api_client.post(
            url, data={"profile_picture": unsupported_file}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_upload_no_file(self, authenticated_api_client):
        url = reverse("v1:profile_picture_upload")
        response = authenticated_api_client.post(url, data={})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "No file was uploaded."

    def test_upload_profile_picture_too_large(
        self, authenticated_api_client, create_large_image
    ):
        url = reverse("v1:profile_picture_upload")
        response = authenticated_api_client.post(
            url, data={"profile_picture": create_large_image}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "File size must be less than 5MB."


@pytest.mark.django_db
class TestCustomVerifyEmailView:
    def test_verify_email_success(
        self, authenticated_api_client, email_confirmation_setup
    ):
        url = reverse("v1:rest_verify_email")
        data = {"key": email_confirmation_setup.key}
        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Email successfully verified"
        assert response.data["email"] == email_confirmation_setup.email_address.email

        email_confirmation_setup.email_address.refresh_from_db()
        assert email_confirmation_setup.email_address.verified is True

    def test_verify_email_invalid_key(self, authenticated_api_client):
        url = reverse("v1:rest_verify_email")
        data = {"key": "invalid-key"}
        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "key" in response.data
        assert response.data["key"][0] == "Invalid verification key"

    def test_verify_already_verified_email(
        self, authenticated_api_client, email_confirmation_setup
    ):
        email_confirmation_setup.email_address.verified = True
        email_confirmation_setup.email_address.save()

        url = reverse("v1:rest_verify_email")
        data = {"key": email_confirmation_setup.key}
        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Email already verified"

    def test_verify_email_expired_key(self, authenticated_api_client, user):
        email_address = EmailAddress.objects.create(
            user=user, email=user.email, verified=False, primary=True
        )
        confirmation = EmailConfirmation.objects.create(
            email_address=email_address,
            created=timezone.now() - timedelta(days=4),
            sent=timezone.now() - timedelta(days=4),
            key=f"{user_pk_to_url_str(user)}abcdef123456",
        )

        url = reverse("v1:rest_verify_email")
        data = {"key": confirmation.key}
        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "key" in response.data
        assert response.data["key"][0] == "Verification key has expired"


@pytest.mark.django_db
class TestConfirmDeletionView:
    def test_confirm_deletion_success(self, authenticated_api_client, user):
        signer = Signer()
        token = signer.sign(user.id)

        EmailAddress.objects.create(
            user=user, email=user.email, primary=True, verified=True
        )

        url = reverse("v1:confirm_deletion")
        response = authenticated_api_client.post(f"{url}?token={token}")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"detail": "User deleted successfully."}

        assert (
            "sessionid" not in response.cookies
            or response.cookies["sessionid"].value == ""
        )
        assert (
            "csrftoken" not in response.cookies
            or response.cookies["csrftoken"].value == ""
        )
        assert (
            "jwt-auth" not in response.cookies
            or response.cookies["jwt-auth"].value == ""
        )
        assert (
            "jwt-refresh-token" not in response.cookies
            or response.cookies["jwt-refresh-token"].value == ""
        )

        user.refresh_from_db()
        assert user.is_active is False
        assert user.username.startswith("deleted_")
        assert len(user.username.split("_")[1]) == 10
        assert user.username.split("_")[1].isalpha()
        assert user.email == f"deleted_{user.id}@deleted.com"
        assert user.first_name == "Deleted"
        assert user.last_name == "User"

        assert not EmailAddress.objects.filter(user=user).exists()

    def test_confirm_deletion_invalid_token(self, authenticated_api_client, user):
        url = reverse("v1:confirm_deletion")
        invalid_token = "invalid-token"
        response = authenticated_api_client.post(f"{url}?token={invalid_token}")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"detail": "Invalid token."}

    def test_confirm_deletion_unauthorized(self, api_client, user):
        signer = Signer()
        token = signer.sign(user.id)

        url = reverse("v1:confirm_deletion")
        response = api_client.post(f"{url}?token={token}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestContactUsView:
    def setup_method(self, method):
        self.admin_user = User.objects.create_superuser(
            username="admin@example.com",
            email="admin@example.com",
            password="testpass123",
            is_active=True,
        )
        self.url = reverse("v1:contact_us")

    def test_successful_contact_submission(self, authenticated_api_client):
        valid_payload = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone_number": "+1234567890",
            "message": "This is a test message",
        }

        response = authenticated_api_client.post(self.url, valid_payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["detail"] == "Contact Us submission received."

    def test_invalid_email_format(self, authenticated_api_client):
        invalid_payload = {
            "name": "John Doe",
            "email": "invalid-email",
            "phone_number": "+1234567890",
            "message": "This is a test message",
        }

        response = authenticated_api_client.post(
            self.url, invalid_payload, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_required_fields(self, authenticated_api_client):
        invalid_payload = {"name": "John Doe", "email": "john@example.com"}

        response = authenticated_api_client.post(
            self.url, invalid_payload, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_empty_message(self, authenticated_api_client):
        invalid_payload = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone_number": "+1234567890",
            "message": "",
        }

        response = authenticated_api_client.post(
            self.url, invalid_payload, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_inactive_admin_no_email(self, authenticated_api_client):
        inactive_admin = User.objects.create_superuser(
            username="inactive@example.com",
            email="inactive@example.com",
            password="testpass123",
            is_active=False,
        )

        valid_payload = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone_number": "+1234567890",
            "message": "This is a test message",
        }

        response = authenticated_api_client.post(self.url, valid_payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        recipient_emails = [email.to[0] for email in mail.outbox]
        assert inactive_admin.email not in recipient_emails

    def test_html_content_in_email(self, authenticated_api_client):
        valid_payload = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone_number": "+1234567890",
            "message": "This is a test message",
        }

        response = authenticated_api_client.post(self.url, valid_payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        email = mail.outbox[0]
        html_content = email.alternatives[0][0]

        assert "<!DOCTYPE html>" in html_content
        assert "Contact Us Submission" in html_content

        assert valid_payload["name"] in html_content
        assert valid_payload["email"] in html_content
        assert valid_payload["phone_number"] in html_content
        assert valid_payload["message"] in html_content
