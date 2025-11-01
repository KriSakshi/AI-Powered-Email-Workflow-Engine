# app/config.py
import os
from dotenv import load_dotenv
load_dotenv()

# Email credentials from .env (your test inbox)
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# Azure OpenAI API credentials
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")

# Gmail IMAP/SMTP settings
IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

# Database and file directories
DATABASE_URL = "sqlite:///./app/email_agent.db"
PDF_OUTPUT_DIR = "./app/generated_pdfs"
ATTACHMENTS_DIR = "./app/attachments"

# ✅ NEW: Only process emails that COME FROM these senders
ALLOWED_SENDERS = {
    "support@aurainsot.tech",
    "quote12399@gmail.com"
}
