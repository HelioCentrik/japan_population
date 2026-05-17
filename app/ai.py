# app/ai.py
"""
Gemini Flash integration for the AI Q&A side panel.

Public API:
    ask_gemini(question, history) -> str
        Returns the model's response text, or an "ERROR: ..." string on failure.

History format (stored in dcc.Store — strings in parts list):
    [{"role": "user" | "model", "parts": ["message text"]}, ...]

The SDK expects parts as dicts ({"text": "..."}), so we convert on the way in.
"""

import os
from pathlib import Path

from google import genai
from google.genai import types

from app.config import AI_MODEL_NAME, AI_MAX_TOKENS, AI_HISTORY_LIMIT



# ── System prompt ─────────────────────────────────────────────────────────────
# Loaded once at import time. AGENT.md is authoritative — rules, schema, metric
# definitions. knowledge/*.md files are additive context: narrative, historical
# background, and source detail. All files concatenated in alphabetical order.

AGENT_MD = Path("AGENT.md").read_text(encoding="utf-8")
_knowledge = sorted(Path("knowledge").glob("*.md"))
_knowledge_text = "\n\n---\n\n".join(p.read_text(encoding="utf-8") for p in _knowledge)
SYSTEM_PROMPT = f"{AGENT_MD}\n\n---\n\n{_knowledge_text}" if _knowledge_text else AGENT_MD


# ── Public API ────────────────────────────────────────────────────────────────

def ask_gemini(question: str, history: list) -> str:
    """
    Send a question to Gemini Flash with conversation history.

    Args:
        question: The user's current question.
        history:  Prior turns from dcc.Store:
                  [{"role": "user"|"model", "parts": ["text"]}, ...]

    Returns:
        Response text string, or "ERROR: <message>" on failure.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "ERROR: GEMINI_API_KEY environment variable is not set."

    try:
        client = genai.Client(api_key=api_key)

        # Build contents list from stored history + new question.
        # Storage uses plain strings in parts; SDK expects {"text": "..."} dicts.
        trimmed = history[-AI_HISTORY_LIMIT:] if len(history) > AI_HISTORY_LIMIT else history
        contents = [
            {"role": turn["role"], "parts": [{"text": turn["parts"][0]}]}
            for turn in trimmed
        ]
        contents.append({"role": "user", "parts": [{"text": question}]})

        response = client.models.generate_content(
            model=AI_MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=AI_MAX_TOKENS,
            ),
        )
        return response.text

    except Exception as e:
        return f"ERROR: {e}"