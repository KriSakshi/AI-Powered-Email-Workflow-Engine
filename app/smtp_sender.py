# app/smtp_sender.py
import smtplib, os
from email.message import EmailMessage
from email.utils import formataddr
from app.config import SMTP_HOST, SMTP_PORT, EMAIL_USER, EMAIL_PASS
from app.logger import logger

def send_email(to_address, subject, body, attachment_path=None):
    msg = EmailMessage()
    # Professional display name
    msg["From"] = formataddr(("Aura Client Support", EMAIL_USER))
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.set_content(body)

    if attachment_path:
        try:
            with open(attachment_path, "rb") as f:
                data = f.read()
            msg.add_attachment(
                data, maintype="application", subtype="pdf",
                filename=os.path.basename(attachment_path)
            )
        except Exception:
            logger.exception("Attachment failed")

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        # NOTE: No BCC and no IMAP APPEND — Gmail auto-saves to Sent, avoiding duplicates
        logger.info(f"Sent email to {to_address}")
        return True
    except Exception:
        logger.exception("SMTP send failed")
        return False
