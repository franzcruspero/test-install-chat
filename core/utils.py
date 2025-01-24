import os
from typing import Any, Optional

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail, EmailMultiAlternatives
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError


def send_email(
    request: HttpRequest,
    subject: str,
    template: str,
    recipients: list[str],
    data: dict[str, Any] = {},
    attachments: Optional[list[Any]] = None,
):
    """
    This function sends an email using a selected template.
    Arguments:
        subject: the subject of the email
        template: the template to be used for the email
        recipient: a list of recipients the email will be sent to
        data: a dictionary to be added as context variables in the email
    """
    context = {
        "current_site": Site.objects.get_current(),
        "protocol": request.scheme,
    }
    context.update(data)
    html_content = render_to_string(template, context)
    text_content = strip_tags(html_content)

    if attachments:
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
        )
        email.attach_alternative(html_content, "text/html")

        for attachment in attachments:
            if hasattr(attachment, "read"):
                filename = getattr(attachment, "name", "attachment")
                content = attachment.read()
                mimetype = getattr(
                    attachment, "content_type", "application/octet-stream"
                )
                email.attach(filename, content, mimetype)
            elif isinstance(attachment, tuple) and len(attachment) == 3:
                email.attach(*attachment)
            else:
                raise ValidationError(f"Invalid attachment type: {type(attachment)}")

        email.send(fail_silently=False)
    else:
        send_mail(
            subject=subject,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
            html_message=html_content,
        )


def get_upload_path(instance: object, filename: str) -> str:
    return os.path.join(instance.__class__.__name__.lower(), filename)
