# app/main.py
from app.logger import logger
from app.db import init_db, log_email
from app.imap_reader import fetch_unseen
from app.classifier import classify_email
from app.support_agent import handle_support
from app.quote_agent import handle_quote

def process(msg):
    sender = msg["sender"]; subject = msg["subject"]; body = msg["body"]
    label = classify_email(sender, subject, body)  # Azure OpenAI intent classification (with fallback)
    logger.info(f"Classified as {label}")
    if label == "Support":
        return handle_support(msg)
    if label == "Quote":
        return handle_quote(msg)
    log_email(sender, subject, body, "Other", "ignored")
    return {"action": "ignored"}

def run_once():
    logger.info("Starting Email Agent (single-run). Fetching unseen emails...")
    init_db()
    processed = 0
    for m in fetch_unseen():  # only emails to support@ / quote@ (filtered in imap_reader)
        try:
            res = process(m)
            processed += 1
            logger.info(f"Processed: {res.get('action')}")
        except Exception:
            logger.exception("Per-message failure")
    logger.info(f"Done. Processed {processed} email(s). Exiting.")

if __name__ == "__main__":
    # Processing starts ONLY when you run main.py, then exits after one pass.
    run_once()
