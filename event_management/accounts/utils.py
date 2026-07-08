import logging
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from .models import CustomUser

logger = logging.getLogger(__name__)


def send_verification_email(user: CustomUser, request=None):
    code = user.email_verification_token
    subject = 'Your EventHub verification code'
    html_message = render_to_string(
        'accounts/verify_email_email.html',
        {'user': user, 'code': code}
    )
    plain_message = strip_tags(html_message)
    try:
        send_mail(
            subject, plain_message,
            settings.DEFAULT_FROM_EMAIL or 'EventHub <onboarding@resend.dev>',
            [user.email], html_message=html_message,
        )
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {e}")


def send_reset_code_email(user: CustomUser, request=None):
    code = user.reset_code
    subject = 'Your EventHub password reset code'
    html_message = render_to_string(
        'accounts/password_reset_email.html',
        {'user': user, 'code': code}
    )
    plain_message = strip_tags(html_message)
    try:
        send_mail(
            subject, plain_message,
            settings.DEFAULT_FROM_EMAIL or 'EventHub <onboarding@resend.dev>',
            [user.email], html_message=html_message,
        )
    except Exception as e:
        logger.error(f"Failed to send reset code to {user.email}: {e}")
