from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from pytest_factoryboy import register
from rest_framework.test import APIClient
from users.tests.factories import UserFactory
from allauth.account.models import EmailAddress, EmailConfirmation
from allauth.account.utils import user_pk_to_url_str
from django.utils import timezone
from rest_framework.authtoken.models import Token
from allauth.socialaccount.models import SocialAccount

register(UserFactory)


@pytest.fixture
def api_client():
    api_client = APIClient()
    yield api_client


@pytest.fixture
def authenticated_api_client(api_client, user):
    api_client.force_authenticate(user=user)
    yield api_client


@pytest.fixture
def admin_client(client, admin_user):
    client.force_login(admin_user)
    yield client


@pytest.fixture
def single_attachment():
    return SimpleUploadedFile(
        "test_attachment.txt",
        b"This is a test attachment content",
        content_type="text/plain",
    )


@pytest.fixture
def create_dummy_image(file_type: str = "jpeg"):
    image_buffer = BytesIO()
    image = Image.new("RGB", (100, 100))
    image.save(image_buffer, file_type)
    image_buffer.name = "dummy." + file_type
    image_buffer.seek(0)
    return image_buffer


@pytest.fixture
def create_large_image(file_type: str = "jpeg", size: int = 6 * 1024 * 1024):
    """Create a dummy image larger than 5MB."""
    image_buffer = BytesIO()
    image = Image.new("RGB", (1000, 1000))
    image.save(image_buffer, file_type)
    image_buffer.name = "large_dummy." + file_type
    image_buffer.seek(0)

    image_buffer.write(b"\0" * (size - image_buffer.getbuffer().nbytes))
    image_buffer.seek(0)

    return image_buffer


@pytest.fixture
def multiple_attachments():
    return [
        SimpleUploadedFile(
            "attachment1.txt",
            b"Content of attachment 1",
            content_type="text/plain",
        ),
        SimpleUploadedFile(
            "attachment2.pdf",
            b"Content of attachment 2",
            content_type="application/pdf",
        ),
        ("attachment3.csv", b"Content of attachment 3", "text/csv"),
    ]

@pytest.fixture
def email_confirmation_setup(authenticated_api_client, user):
    email_address = EmailAddress.objects.create(
        user=user,
        email=user.email,
        verified=False,
        primary=True
    )
    confirmation = EmailConfirmation.objects.create(
        email_address=email_address,
        created=timezone.now(),
        sent=timezone.now(),
        key=f"{user_pk_to_url_str(user)}abcdef123456"
    )
    return confirmation 

@pytest.fixture(autouse=True)
def setup(settings):
    settings.ACCOUNT_EMAIL_VERIFICATION = "optional"
    settings.ACCOUNT_EMAIL_REQUIRED = True
@pytest.fixture
def social_account(user):
    return SocialAccount.objects.create(user=user, provider="google")