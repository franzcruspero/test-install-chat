import pytest

from core.utils import get_upload_path, send_email


@pytest.mark.django_db
def test_send_email(request, mailoutbox):
    request.scheme = "http"

    send_email(
        request,
        "subject",
        "account/email/password_reset_key_message.txt",
        ["to@example.com"],
    )

    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == "subject"
    assert mailoutbox[0].to == ["to@example.com"]


@pytest.mark.django_db
def test_send_email_with_attachment(request, mailoutbox, single_attachment):
    request.scheme = "http"

    send_email(
        request,
        "subject with attachment",
        "account/email/password_reset_key_message.txt",
        ["to@example.com"],
        attachments=[single_attachment],
    )

    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == "subject with attachment"
    assert mailoutbox[0].to == ["to@example.com"]
    assert len(mailoutbox[0].attachments) == 1
    assert mailoutbox[0].attachments[0][0] == "test_attachment.txt"
    assert mailoutbox[0].attachments[0][1] == "This is a test attachment content"
    assert mailoutbox[0].attachments[0][2] == "text/plain"


@pytest.mark.django_db
def test_send_email_with_multiple_attachments(
    request, mailoutbox, multiple_attachments
):
    request.scheme = "http"

    send_email(
        request,
        "subject with multiple attachments",
        "account/email/password_reset_key_message.txt",
        ["to@example.com"],
        attachments=multiple_attachments,
    )

    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == "subject with multiple attachments"
    assert mailoutbox[0].to == ["to@example.com"]
    assert len(mailoutbox[0].attachments) == 3

    assert mailoutbox[0].attachments[0][0] == "attachment1.txt"
    assert mailoutbox[0].attachments[0][2] == "text/plain"

    assert mailoutbox[0].attachments[1][0] == "attachment2.pdf"
    assert mailoutbox[0].attachments[1][2] == "application/pdf"

    assert mailoutbox[0].attachments[2][0] == "attachment3.csv"
    assert mailoutbox[0].attachments[2][2] == "text/csv"


@pytest.mark.django_db
def test_get_upload_path(user):
    assert get_upload_path(user, "test.txt") == "user/test.txt"
