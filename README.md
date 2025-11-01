# Email Agent (Week 5) — BRD Aligned, Single-Run

Env (only these 6): EMAIL_USER, EMAIL_PASS, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_DEPLOYMENT, AZURE_API_VERSION.

## What it does
- Runs **once** when you execute `main.py`.
- Fetches **UNSEEN** emails addressed to **support@** or **quote@** only.
- **Classifies** intent via Azure OpenAI (with **fallback keywords**).
- **Support:** validate → LLM ack → **SMTP send** → log.
- **Quote:** validate required fields → if missing ask; if complete → **simulate Aura**, **generate PDF**, **send** → log.
- **Attachments**: extracted and **saved** in `app/attachments/` for future processing.

## Run
1) `python -m venv venv && source venv/bin/activate`
2) `pip install -r requirements.txt`
3) Copy `.env.example` to `.env`, fill values.
4) `./run.sh` (or `python app/main.py`)
