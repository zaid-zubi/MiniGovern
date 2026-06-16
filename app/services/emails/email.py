import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.config import settings
from core.logging import logger


def send_email(
    recipients: list[str],
    subject: str,
    body: str,
) -> None:
    if not recipients:
        logger.warning("No emails recipients provided")
        return

    try:
        msg = MIMEMultipart()
        msg["From"] = settings.email_from
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(
            settings.smtp_host,
            settings.smtp_port,
        ) as smtp:
            smtp.ehlo()

            if (
                settings.smtp_username
                and settings.smtp_password
            ):
                smtp.starttls()
                smtp.login(
                    settings.smtp_username,
                    settings.smtp_password,
                )

            smtp.sendmail(
                settings.email_from,
                recipients,
                msg.as_string(),
            )

        logger.info(
            "Email sent successfully to %s",
            recipients,
        )

    except Exception:
        logger.exception(
            "Failed to send emails"
        )