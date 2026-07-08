import resend
import logging
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class ResendEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        resend.api_key = settings.RESEND_API_KEY
        count = 0
        for message in email_messages:
            try:
                payload = {
                    "from": settings.DEFAULT_FROM_EMAIL or "onboarding@resend.dev",
                    "to": message.to,
                    "subject": message.subject,
                }
                if message.body:
                    payload["text"] = message.body
                if hasattr(message, "alternatives") and message.alternatives:
                    for alt, ctype in message.alternatives:
                        if ctype == "text/html":
                            payload["html"] = alt
                            break
                if not payload.get("html") and message.body:
                    payload["html"] = message.body.replace("\n", "<br>")
                resend.Emails.send(payload)
                count += 1
            except Exception as e:
                logger.error(f"Resend email failed to {message.to}: {e}")
                if not self.fail_silently:
                    raise
        return count