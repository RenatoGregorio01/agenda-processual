import logging
from email.message import EmailMessage
from email.utils import formataddr

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
    from_name = (settings.smtp_from_name or "").strip()
    message["From"] = (
        formataddr((from_name, settings.smtp_from)) if from_name else settings.smtp_from
    )
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(text_body)
    if html_body:
        message.add_alternative(html_body, subtype="html")

    username = settings.smtp_user.strip() or None
    password = settings.smtp_password.strip() or None

    # 465 = TLS implícito (use_tls); 587 = STARTTLS (smtp_tls).
    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=username,
        password=password,
        start_tls=settings.smtp_tls and not settings.smtp_ssl,
        use_tls=settings.smtp_ssl,
    )
    logger.info("E-mail enviado")
