import logging
from email.message import EmailMessage

import aiosmtplib

from app.core.config import Settings

logger = logging.getLogger(__name__)


async def send_email(
    *,
    settings: Settings,
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str | None = None,
) -> None:
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(text_body)
    if html_body:
        message.add_alternative(html_body, subtype="html")

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user or None,
        password=settings.smtp_password or None,
        start_tls=settings.smtp_tls,
    )
    logger.info("E-mail enviado para %s: %s", to_email, subject)
