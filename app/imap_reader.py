# app/imap_reader.py
import os
import time
import uuid
import imaplib
import email
from email.header import decode_header
from app.config import (
    IMAP_HOST, IMAP_PORT, EMAIL_USER, EMAIL_PASS,
    ATTACHMENTS_DIR, ALLOWED_SENDERS
)
from app.logger import logger

os.makedirs(ATTACHMENTS_DIR, exist_ok=True)

def _decode_header(value: str) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    out = ""
    for text, cs in parts:
        if isinstance(text, bytes):
            out += text.decode(cs or "utf-8", errors="ignore")
        else:
            out += text
    return out

def _connect():
    m = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    m.login(EMAIL_USER, EMAIL_PASS)
    return m

def _is_allowed_sender(msg) -> bool:
    sender = (msg.get("From") or "").lower()
    return any(allowed in sender for allowed in ALLOWED_SENDERS)

def _safe_filename(name: str | None) -> str:
    name = name or f"attachment_{uuid.uuid4().hex}"
    return "".join(c for c in name if c.isalnum() or c in (" ", ".", "_", "-")).strip()

def fetch_unseen():
    """
    Single-shot fetch:
    - Reads UNSEEN emails in INBOX
    - Keeps only those whose **sender** is in ALLOWED_SENDERS
    - Saves attachments to ATTACHMENTS_DIR (once per real attachment)
    - Marks processed messages as \\Seen to avoid reprocessing
    """
    mail = _connect()
    mail.select("INBOX")
    typ, data = mail.search(None, "UNSEEN")
    if typ != "OK":
        mail.logout()
        return []

    messages = []
    ids = data[0].split() if data and data[0] else []
    for num in ids:
        typ, msg_data = mail.fetch(num, "(RFC822)")
        if typ != "OK" or not msg_data or not msg_data[0]:
            continue

        # Mark this message as seen so we don't process/save attachments twice on next run
        try:
            mail.store(num, "+FLAGS", "\\Seen")
        except Exception:
            # non-fatal
            pass

        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)

        # Filter by allowed sender BEFORE doing any work
        if not _is_allowed_sender(msg):
            continue

        sender = _decode_header(msg.get("From"))
        subject = _decode_header(msg.get("Subject"))
        body = ""
        saved_files = []

        for part in msg.walk():
            dispo = part.get_content_disposition()  # 'attachment', 'inline', or None
            ctype = part.get_content_type()
            filename = part.get_filename()

            # Body: only take text/plain that is NOT an attachment
            if ctype == "text/plain" and dispo != "attachment":
                payload = part.get_payload(decode=True)
                if payload:
                    body += payload.decode(part.get_content_charset() or "utf-8", errors="ignore")

            # Attachments: save only when disposition says 'attachment' and filename exists
            elif dispo == "attachment" and filename:
                try:
                    payload = part.get_payload(decode=True)
                    if not payload:
                        continue
                    base = _safe_filename(filename)
                    unique = f"{int(time.time())}_{uuid.uuid4().hex}_{base}"
                    path = os.path.join(ATTACHMENTS_DIR, unique)
                    with open(path, "wb") as f:
                        f.write(payload)
                    saved_files.append(path)
                except Exception:
                    # continue even if one attachment fails
                    logger.exception("Failed saving attachment")

        messages.append({
            "sender": sender,
            "subject": subject,
            "body": body,
            "attachments": saved_files,  # full saved paths
            "raw": raw
        })

    mail.logout()
    logger.info(f"Fetched {len(messages)} UNSEEN email(s) from allowed senders; attachments saved where present")
    return messages
