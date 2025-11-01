# app/classifier.py
from app.azure_openai_client import azure_chat_completion

KW = {
    "quote": ["quote", "quotation", "premium", "proposal", "pricing", "insure", "insurance"],
    "support": ["error", "issue", "support", "help", "problem", "unable", "bug", "question"]
}

def fallback(subject, body):
    text = (subject + " " + body).lower()
    sq = sum(text.count(k) for k in KW["quote"])
    ss = sum(text.count(k) for k in KW["support"])
    if sq >= ss and sq > 0: return "Quote"
    if ss > sq: return "Support"
    return "Other"

def classify_email(sender, subject, body):
    system = "Classify the email into exactly one: Support, Quote, Other. Return only that word."
    user = f"Sender: {sender}\nSubject: {subject}\nBody:\n{body}\nLabel:"
    try:
        out = azure_chat_completion(system, user, max_tokens=10, temperature=0)
        label = out.strip().split()[0].capitalize()
        if label not in ("Support", "Quote", "Other"):
            return fallback(subject, body)
        return label
    except Exception:
        # Fallback if OpenAI API is down/unreachable
        return fallback(subject, body)
