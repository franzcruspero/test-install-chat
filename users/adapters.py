from typing import Optional

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailConfirmation
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.http import HttpRequest
from django.template.loader import render_to_string


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(
        self, request: Optional[HttpRequest], emailconfirmation: EmailConfirmation
    ) -> str:
        """
        Constructs the email confirmation (activation) url.
        Note that if you have architected your system such that email confirmations
        are sent outside of the request context `request` can be `None` here.
        """
        key = emailconfirmation.key
        verify_email_url = f"{settings.FRONTEND_URL}/settings/email/verify?token={key}"
        return verify_email_url

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """
        Sends the email confirmation mail.
        """
        context = {
            "user": emailconfirmation.email_address.user,
            "verify_email_url": self.get_email_confirmation_url(
                request, emailconfirmation
            ),
            "current_site": get_current_site(request),
            "key": emailconfirmation.key,
        }
        if signup:
            email_template = "account/email/email_confirmation_signup_message"
        else:
            email_template = "account/email/email_confirmation_message"

        html_content = render_to_string(f"{email_template}.html", context)
        text_content = render_to_string(f"{email_template}.txt", context)

        email = EmailMultiAlternatives(
            subject="Email Verification",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[emailconfirmation.email_address.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
