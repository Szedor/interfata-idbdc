# grant_navigator/engine/ai_core.py
"""
Motor AI central — toate apelurile către Claude API trec prin acest modul.
Folosește claude-haiku-4-5 (cel mai economic) pentru interogări rapide
și claude-sonnet-4-6 pentru generare documente complexe.
"""

import streamlit as st
import requests
import json


CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
MODEL_FAST     = "claude-haiku-4-5-20251001"    # interogări, analiză
MODEL_SMART    = "claude-sonnet-4-6"             # generare documente


def _get_api_key() -> str:
    key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not key:
        st.error("ANTHROPIC_API_KEY lipsă în Streamlit Secrets. Adaugă cheia în Settings → Secrets.")
        st.stop()
    return key


def _call_claude(
    system_prompt: str,
    user_message: str,
    model: str = MODEL_FAST,
    max_tokens: int = 1500,
) -> str:
    """
    Apel direct către Claude API. Returnează textul răspunsului.
    """
    api_key = _get_api_key()

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_message}
        ],
    }

    try:
        resp = requests.post(CLAUDE_API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        blocks = data.get("content", [])
        return " ".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()
    except requests.exceptions.Timeout:
        return "⚠️ Timeout — serverul AI nu a răspuns în timp util. Încearcă din nou."
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if e.response else "?"
        if code == 401:
            return "⚠️ Cheie API invalidă. Verifică ANTHROPIC_API_KEY în Secrets."
        if code == 429:
            return "⚠️ Limită de utilizare depășită. Încearcă peste câteva secunde."
        return f"⚠️ Eroare API ({code}): {e}"
    except Exception as e:
        return f"⚠️ Eroare neașteptată: {e}"


def _call_claude_stream(
    system_prompt: str,
    user_message: str,
    model: str = MODEL_FAST,
    max_tokens: int = 1500,
    placeholder=None,
):
    """
    Apel cu streaming — afișează răspunsul token cu token.
    Dacă placeholder este un st.empty(), actualizează live.
    Returnează textul complet.
    """
    api_key = _get_api_key()

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "stream": True,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_message}
        ],
    }

    full_text = ""

    try:
        with requests.post(
            CLAUDE_API_URL, headers=headers, json=payload,
            stream=True, timeout=90
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                decoded = line.decode("utf-8")
                if decoded.startswith("data:"):
                    raw = decoded[5:].strip()
                    if raw == "[DONE]":
                        break
                    try:
                        event = json.loads(raw)
                        if event.get("type") == "content_block_delta":
                            delta = event.get("delta", {})
                            if delta.get("type") == "text_delta":
                                chunk = delta.get("text", "")
                                full_text += chunk
                                if placeholder:
                                    placeholder.markdown(full_text + "▌")
                    except json.JSONDecodeError:
                        continue

        if placeholder:
            placeholder.markdown(full_text)
        return full_text

    except Exception as e:
        err = f"⚠️ Eroare streaming: {e}"
        if placeholder:
            placeholder.markdown(err)
        return err


# =========================================================
# FUNCȚII HELPER PENTRU DATE IDBDC
# =========================================================

def safe_fetch(supabase, table: str, limit: int = 300) -> list[dict]:
    try:
        res = supabase.table(table).select("*").limit(limit).execute()
        return res.data or []
    except Exception:
        return []


def df_to_context(rows: list[dict], max_rows: int = 50) -> str:
    """Convertește rânduri din BD în text context pentru Claude."""
    if not rows:
        return "(fără date)"
    sample = rows[:max_rows]
    lines  = []
    for r in sample:
        parts = [f"{k}={v}" for k, v in r.items() if v is not None and str(v).strip()]
        lines.append(" | ".join(parts))
    result = "\n".join(lines)
    if len(rows) > max_rows:
        result += f"\n... și încă {len(rows) - max_rows} înregistrări."
    return result
