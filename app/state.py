# app/state.py
"""Shared runtime state flags for the orchestration layer."""

from app.data import figure_cache



def is_ready() -> bool:
    """True when the figure cache fingerprint is valid.

    Uses figure_cache.is_valid() rather than a threading.Event so this works
    correctly across all Gunicorn worker processes — every worker reads the
    same fingerprint file on disk.
    """
    return figure_cache.is_valid()