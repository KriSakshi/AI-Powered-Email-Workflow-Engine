# app/quote_agent.py
import re
import json
import uuid
from app.db import log_email
from app.logger import logger
from app.smtp_sender import send_email
from app.azure_openai_client import azure_chat_completion
from app.aura_client import AuraClient
from app.pdf_generator import generate_quote_pdf

# Required fields per BRD
REQ = ["client_name", "employee_count", "insurance_type"]

def _extract_email(addr):
    m = re.search(r"<([^>]+)>", addr or "")
    return m.group(1) if m else (addr or "").strip()

def _quick_extract(text):
    """Try to extract fields using simple regex patterns."""
    d = {}
    m = re.search(r"(?:client|client name|company name)[:\-]\s*([A-Za-z0-9 &.,'-]+)", text, re.I)
    if m: d["client_name"] = m.group(1).strip()
    m = re.search(r"(?:employees|employee count|no of employees)[:\-]\s*(\d+)", text, re.I)
    if m: d["employee_count"] = int(m.group(1))
    m = re.search(r"(?:insurance type|type)[:\-]\s*([A-Za-z ]+)", text, re.I)
    if m: d["insurance_type"] = m.group(1).strip()
    return d

def _missing(d):
    return [k for k in REQ if k not in d or not d[k]]

def handle_quote(email_obj):
    sender = email_obj["sender"]
    subject = email_obj["subject"]
    body = email_obj["body"]
    attachments = email_obj.get("attachments", [])
    to_email = _extract_email(sender)

    # Step 1: extract basic info
    details = _quick_extract(subject + "\n" + body)
    _ = attachments  # saved for audit but not parsed (BRD-safe)

    # Step 2: check missing fields
    miss = _missing(details)
    if miss:
        # Attempt LLM extraction for missing fields
        try:
            sys = "Extract client_name, employee_count, insurance_type as JSON keys from this email. If unknown, omit key."
            out = azure_chat_completion(sys, body, max_tokens=150)
            try:
                j = json.loads(out)
                details.update({k: v for k, v in j.items() if k in REQ and v})
            except Exception:
                pass
        except Exception:
            pass

    miss = _missing(details)
    if miss:
        # Step 3: Request missing info
        reply = (
            "Hello,\n\n"
            f"To prepare your quotation, please provide: {', '.join(miss)}.\n"
            "Example:\n"
            "Client Name: ACME Corp\n"
            "Employee Count: 45\n"
            "Insurance Type: Health\n\n"
            "Regards,\nAura Quote Team"
        )
        sent = send_email(to_email, "More details required for your quote", reply)
        log_email(sender, subject, body, "Quote", "requested_missing_details")
        return {"action": "requested_missing_details", "reply": reply, "sent": sent}

    # Step 4: If details complete, simulate quote creation
    try:
        aura = AuraClient()
        aura.login()
        resp = aura.create_quote(details)
        quote_id = resp.get("id", str(uuid.uuid4()))
        pdf = generate_quote_pdf(quote_id, {**details, **resp})
        reply = (
            f"Hello,\n\nAttached is your quotation (Quote ID: {quote_id}). "
            f"Your calculated premium is {resp.get('premium')}.\n\n"
            "Regards,\nAura Quote Team"
        )
        sent = send_email(to_email, f"Aura Quotation - {quote_id}", reply, attachment_path=pdf)
        log_email(sender, subject, body, "Quote", "created_quote_and_sent" if sent else "created_quote_but_send_failed")
        return {
            "action": "created_quote_and_sent" if sent else "created_quote_but_send_failed",
            "pdf": pdf,
            "sent": sent
        }
    except Exception:
        logger.exception("Quote flow failed")
        reply = (
            "Hello,\n\nWe couldn't generate the quote automatically. "
            "Our team will follow up soon.\n\n"
            "Regards,\nAura Quote Team"
        )
        sent = send_email(to_email, "Quote processing issue", reply)
        log_email(sender, subject, body, "Quote", "failed_quote")
        return {"action": "failed_quote", "reply": reply, "sent": sent}
