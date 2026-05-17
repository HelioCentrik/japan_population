# callbacks/ai.py
from dash import html, dcc, Input, Output, State, no_update

from dash_app import app
from app.aesthetics.config import AI_HISTORY_LIMIT
from app.ai import ask_gemini


def _render_conversation(history: list) -> list:
    """Build Dash children from Gemini-format conversation history.

    Each turn in history is {"role": "user"|"model", "parts": ["text"]}.
    Error responses (prefixed "ERROR:") get a distinct CSS class.
    """
    children = []
    for turn in history:
        role = turn.get("role", "")
        text = turn.get("parts", [""])[0]
        is_error = role == "model" and text.startswith("ERROR:")

        if role == "user":
            children.append(html.Div(
                dcc.Markdown(text, className="ai-msg-text"),
                className="ai-msg ai-msg-user",
            ))
        elif role == "model":
            children.append(html.Div(
                dcc.Markdown(text, className="ai-msg-text"),
                className="ai-msg ai-msg-error" if is_error else "ai-msg ai-msg-model",
            ))
    return children


@app.callback(
    Output("ai-chat-output", "children", allow_duplicate=True),
    Input("ai-chat-history", "data"),
    prevent_initial_call="initial_duplicate",
)
def restore_chat_on_load(history):
    if not history:
        return no_update
    return _render_conversation(history)


@app.callback(
    Output("ai-pending-question", "data"),
    Output("ai-input", "value"),
    Output("ai-chat-output", "children", allow_duplicate=True),
    Input("ai-submit-btn", "n_clicks"),
    State("ai-input", "value"),
    State("ai-chat-history", "data"),
    prevent_initial_call=True,
)
def submit_question(n_clicks, question, history):
    if not question or not question.strip():
        return no_update, no_update, no_update
    q = question.strip()
    preview = history + [{"role": "user", "parts": [q]}]
    return q, "", _render_conversation(preview)


@app.callback(
    Output("ai-chat-output", "children"),
    Output("ai-chat-history", "data"),
    Output("ai-thinking-indicator", "children"),
    Input("ai-pending-question", "data"),
    State("ai-chat-history", "data"),
    prevent_initial_call=True,
)
def fetch_ai_response(question, history):
    if not question:
        return no_update, no_update, no_update

    response = ask_gemini(question, history)

    new_history = history + [
        {"role": "user",  "parts": [question]},
        {"role": "model", "parts": [response]},
    ]
    new_history = new_history[-AI_HISTORY_LIMIT:]

    return _render_conversation(new_history), new_history, None
