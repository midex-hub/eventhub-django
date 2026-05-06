import uuid
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from .models import CustomUser


def generate_verification_token():
    """Generate a unique email verification token."""
    return str(uuid.uuid4())


def send_verification_email(user: CustomUser, request):
    """Send email verification email to user."""
    token = generate_verification_token()
    user.email_verification_token = token
    user.save(update_fields=['email_verification_token'])
    
    verify_url = request.build_absolute_uri(
        reverse('verify_email', kwargs={'token': token})
    )
    
    subject = 'Verify your email address'
    html_message = render_to_string(
        'accounts/verify_email_email.html',
        {'user': user, 'verify_url': verify_url}
    )
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        'noreply@eventhub.com', 
        [user.email],
        html_message=html_message,
    )
