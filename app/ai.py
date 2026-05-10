# app/ai.py
"""
Gemini Flash integration for the AI Q&A side panel.

Public API:
    ask_gemini(question, history) -> str
        Returns the model's response text, or an "ERROR: ..." string on failure.

History format (matches Gemini's native schema — store as-is in dcc.Store):
    [{"role": "user" | "model", "parts": ["message text"]}, ...]
"""

import os
from pathlib import Path

import google.generativeai as genai

from app.config import AI_MODEL_NAME, AI_MAX_TOKENS, AI_HISTORY_LIMIT

# ── System prompt ─────────────────────────────────────────────────────────────
# Loaded once at import time. AGENT.md defines the domain model, metric
# definitions, data quirks, and rules the model must follow.

AGENT_MD = Path("AGENT.md").read_text(encoding="utf-8")


# ── Public API ────────────────────────────────────────────────────────────────

def ask_gemini(question: str, history: list) -> str:
    """
    Send a question to Gemini Flash with conversation history.

    Args:
        question: The user's current question.
        history:  List of prior turns in Gemini format:
                  [{"role": "user"|"model", "parts": ["text"]}, ...]

    Returns:
        Response text string, or "ERROR: <message>" on failure.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "ERROR: GEMINI_API_KEY environment variable is not set."

    try:
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel(
            model_name=AI_MODEL_NAME,
            system_instruction=AGENT_MD,
            generation_config=genai.GenerationConfig(
                max_output_tokens=AI_MAX_TOKENS,
            ),
        )

        # Trim history before sending — keep the last N messages.
        # Trimming here (not in the callback) keeps the callback thin.
        trimmed_history = history[-AI_HISTORY_LIMIT:] if len(history) > AI_HISTORY_LIMIT else history

        chat = model.start_chat(history=trimmed_history)
        response = chat.send_message(question)
        return response.text

    except Exception as e:
        return f"ERROR: {e}"