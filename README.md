📧 AI-Powered Email Workflow Engine

An intelligent email workflow built with Python and Azure OpenAI that reads incoming messages, classifies their intent, and automatically sends appropriate responses or quotations.

🧾 Overview

This system automates client-email handling for Aura’s support and quotation inboxes.
It connects to a mailbox, detects whether an email is a Support request, a Quote request, or Other, and then performs the correct action:

Support requests → send a polite acknowledgment.

Quote requests → extract required data, simulate quote creation, generate a PDF, and reply with the document.

Other messages → safely log and ignore.

All actions are stored in a local SQLite database for auditing.

🧱 Architecture
           ┌──────────────────────┐
           │ Email Inbox (IMAP)   │
           └───────────┬──────────┘
                       │
                       ▼
          ┌─────────────────────────┐
          │  IMAP Reader            │
          │  app/imap_reader.py     │
          └───────────┬─────────────┘
                       ▼
          ┌────────────────────────-------
          │  Classifier (LLM + Fallback) │
          │  app/classifier.py           │
          └──────────┬──────────┬────────┘
                     │          │
          ┌──────────▼──┐   ┌───▼────────┐
          │SupportAgent │   │QuoteAgent  │
          │support_agent│   │quote_agent │
          └──────┬──────┘   └────┬───────┘
                 │               │
                 ▼               ▼
       ┌─────────────────┐  ┌───────────────┐
       │ SMTP Sender     │  │ Aura + PDFGen │
       │ smtp_sender.py  │  │ aura/pdf_gen  │
       └────────┬────────┘  └──────┬────────┘
                ▼                  ▼
         ┌───────────────┐   ┌──────────────┐
         │ Reply Sent    │   │ DB Logger    │
         │ (Gmail SMTP)  │   │ app/db.py    |
         └───────────────┘   └──────────────┘

📂 Folder Structure
email-agent/
│
├── app/
│   ├── __init__.py
│   ├── aura_client.py
│   ├── azure_openai_client.py
│   ├── classifier.py
│   ├── config.py
│   ├── db.py
│   ├── imap_reader.py
│   ├── logger.py
│   ├── main.py
│   ├── pdf_generator.py
│   ├── quote_agent.py
│   ├── smtp_sender.py
│   ├── support_agent.py
│   ├── attachments/
│   └── generated_pdfs/
│
├── .env.example
├── requirements.txt
├── .gitignore
├── run.sh
└── README.md

⚙️ Setup
1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

2. Install dependencies
pip install -r requirements.txt

3. Configure environment variables

Copy .env.example to .env and fill in:

EMAIL_USER=<your_email>
EMAIL_PASS=<app_password>
AZURE_OPENAI_ENDPOINT=<endpoint>
AZURE_OPENAI_KEY=<api_key>
AZURE_DEPLOYMENT=<deployment_name>
AZURE_API_VERSION=<api_version>

4. Run
./run.sh
# or
python app/main.py

🔑 Environment Variables
Key	Description
EMAIL_USER	IMAP/SMTP email ID
EMAIL_PASS	App password
AZURE_OPENAI_ENDPOINT	Azure OpenAI endpoint
AZURE_OPENAI_KEY	Azure API key
AZURE_DEPLOYMENT	Model deployment name
AZURE_API_VERSION	API version string


🔁 Workflow

imap_reader.py connects to Gmail IMAP, fetches unseen messages from approved senders, and saves attachments.

classifier.py calls the Azure OpenAI endpoint to label each email as Support, Quote, or Other (with a keyword fallback).

support_agent.py checks if it’s a valid issue and sends a ready-made acknowledgment.

quote_agent.py extracts or requests missing details, simulates quote creation through aura_client.py, generates a PDF via pdf_generator.py, and emails it back.

smtp_sender.py handles sending replies with or without attachments.

db.py logs every processed email (sender, subject, label, action) in a local SQLite database.

The workflow runs once per call of main.py and then exits.

🧰 Tech Stack
Area	Tool / Library
Programming	Python 3.x
AI Model	Azure OpenAI (Chat Completions)
Email	imaplib, smtplib
Database	SQLite + SQLAlchemy
PDF Generation	reportlab
Configuration	python-dotenv
Logging	built-in logging module


🚀 Running a Demo

Send a test mail to one of the allowed addresses (e.g., support@aurainsot.tech or quote@aurainsot.tech).

Execute:

python app/main.py


Observe terminal logs.

Check:

app/generated_pdfs/ for quote PDFs.

app/email_agent.db for DB entries.

Your “Sent” folder for outgoing replies.

🧠 Features

Reads and filters unseen emails automatically.

AI intent detection with fallback logic.

Dedicated support and quotation agents.

Dynamic PDF generation for quotations.

Secure configuration using environment variables.

Database logging for every processed message.

One-run mode for simple scheduling or CI execution.


