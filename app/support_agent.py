# app/support_agent.py
import re
from app.smtp_sender import send_email
from app.db import log_email
from app.logger import logger

def _extract_email(addr):
    m = re.search(r"<([^>]+)>", addr or "")
    return m.group(1) if m else (addr or "").strip()

def _looks_like_support(subject, body):
    text = (subject + " " + body).lower()
    return any(k in text for k in ["error", "issue", "support", "help", "problem", "unable", "bug", "question", "fail", "login"])

def handle_support(email_obj):
    sender = email_obj["sender"]
    subject = email_obj["subject"] or "Your support request"
    body = email_obj["body"] or ""
    to_email = _extract_email(sender)

    # Validate if it's a real support query
    if not _looks_like_support(subject, body):
        log_email(sender, subject, body, "Support", "ignored_invalid_support")
        return {"action": "ignored_invalid_support"}

    # Fixed professional reply (no repetition or AI generation)
    reply = (
        "Hello,\n\n"
        "Thank you for reaching out to Aura Support. We’ve received your request and our team is reviewing it.\n"
        "We’ll get back to you shortly with an update.\n\n"
        "Regards,\nAura Support Team"
    )

    try:
        sent = send_email(to_email, f"Re: {subject}", reply)
        log_email(sender, subject, body, "Support", "sent_support_response" if sent else "support_send_failed")
        return {"action": "sent_support_response" if sent else "support_send_failed", "reply": reply, "sent": sent}
    except Exception as e:
        logger.exception("Support flow failed")
        log_email(sender, subject, body, "Support", "support_send_failed")
        return {"action": "support_send_failed", "error": str(e)}
