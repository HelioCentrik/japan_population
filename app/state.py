# app/state.py
"""Shared runtime state flags for the orchestration layer."""

import threading

# Set by prewarm.run() when the figure cache is fully loaded.
# Checked by the readiness callback to dismiss the loading overlay.
_app_ready = threading.Event()


def is_ready() -> bool:
    return _app_ready.is_set()


def mark_ready() -> None:
    _app_ready.set()