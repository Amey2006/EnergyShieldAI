"""
Unified LLM client so agents don't care which provider is configured.
Set LLM_PROVIDER in .env to "grok", "groq", or "gemini".

- grok  : xAI's API (no guaranteed permanent free tier, pay-as-you-go)
- groq  : Groq's LPU inference API (free tier, fast, great for structured JSON)
- gemini: Google Gemini API (generous free tier)

Every provider is called through `chat_json(system_prompt, user_prompt)` which
asks the model to return ONLY JSON and parses it, so agent code never needs
to know which backend produced the answer.
"""
import os
import json
import httpx
from utils.logger import get_logger

log = get_logger("llm_client")

PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


def _call_grok(system_prompt: str, user_prompt: str) -> str:
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        raise RuntimeError("GROK_API_KEY not set")
    resp = httpx.post(
        "https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "groq/llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _call_groq(system_prompt: str, user_prompt: str) -> str:
    from groq import Groq
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content


def _call_gemini(system_prompt: str, user_prompt: str) -> str:
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "gemini-1.5-flash", system_instruction=system_prompt
    )
    resp = model.generate_content(user_prompt)
    return resp.text


_PROVIDERS = {"grok": _call_grok, "groq": _call_groq, "gemini": _call_gemini}


def chat_json(system_prompt: str, user_prompt: str) -> dict:
    """Call the configured LLM and parse its reply as JSON. Falls back to a
    minimal error dict rather than raising, so a single agent failure doesn't
    take down the whole pipeline."""
    fn = _PROVIDERS.get(PROVIDER)
    if fn is None:
        raise ValueError(f"Unknown LLM_PROVIDER '{PROVIDER}'")

    full_system = (
        system_prompt
        + "\n\nRespond with ONLY valid JSON. No markdown, no preamble, no code fences."
    )
    try:
        raw = fn(full_system, user_prompt)
        cleaned = _strip_code_fences(raw)
        return json.loads(cleaned)
    except Exception as e:
        log.error(f"LLM call failed ({PROVIDER}): {e}")
        return {"error": str(e)}
