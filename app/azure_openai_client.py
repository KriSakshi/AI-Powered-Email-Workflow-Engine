# app/azure_openai_client.py
import requests
from app.config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_DEPLOYMENT, AZURE_API_VERSION
from app.logger import logger

def azure_chat_completion(system_prompt, user_prompt, max_tokens=256, temperature=0.0):
    """
    Azure Chat Completions (2024-12-01-preview and similar):
    - Use 'max_completion_tokens' instead of 'max_tokens'.
    - Keep 'messages' schema.
    """
    if not (AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY and AZURE_DEPLOYMENT and AZURE_API_VERSION):
        raise ValueError("Azure OpenAI env vars missing")

    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_DEPLOYMENT}/chat/completions?api-version={AZURE_API_VERSION}"
    headers = {"Content-Type": "application/json", "api-key": AZURE_OPENAI_KEY}

    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 1,
        # IMPORTANT: Azure preview requires this name
        "max_completion_tokens": max_tokens
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        # For safety, if some deployments still accept 'max_tokens', retry once automatically
        if resp.status_code == 400 and "max_tokens" in resp.text and "unsupported_parameter" in resp.text:
            logger.error("Azure OpenAI error %s %s", resp.status_code, resp.text)
        else:
            logger.error("Azure OpenAI error %s %s", resp.status_code, resp.text)
        raise RuntimeError("Azure OpenAI API error")

    data = resp.json()
    # Standard Azure schema: choices[0].message.content
    return data["choices"][0]["message"]["content"]
