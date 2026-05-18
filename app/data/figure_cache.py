# app/data/figure_cache.py
"""
Disk-backed figure cache with fingerprint-based invalidation.

_store is the in-memory cache (replaces @lru_cache on figure builders).
Disk cache survives process restarts — figures are only rebuilt when the DB changes.
Fingerprint is derived from DB file mtime, so any DB rebuild auto-invalidates.

Public API:
    is_valid()          — True if disk cache matches current DB
    load_all()          — hydrate _store from disk (call on valid cache at startup)
    get(key)            — return cached figure or None
    put(key, fig)       — store in memory only (runtime use)
    save(key, fig)      — store in memory + persist to disk (pre-warm use)
    write_fingerprint() — stamp disk cache after a full build
    clear()             — wipe disk and memory
    make_key(*parts)    — build a filesystem-safe cache key
"""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

from app.utils import CACHE_DIR, DB_PATH


_FINGERPRINT_FILE = CACHE_DIR / "_fingerprint.txt"
_store: dict[str, go.Figure] = {}

# Bump when figure trace structure changes (forces cache rebuild on next start).
_SCHEMA_VERSION = "v3"


def _current_fingerprint() -> str:
    """DB file mtime + schema version — both must match for cache to be valid."""
    return f"{_SCHEMA_VERSION}:{hex(DB_PATH.stat().st_mtime_ns)}"


def is_valid() -> bool:
    """True if the disk cache exists and matches the current DB fingerprint."""
    if not _FINGERPRINT_FILE.exists():
        return False
    try:
        return _FINGERPRINT_FILE.read_text(encoding="utf-8").strip() == _current_fingerprint()
    except OSError:
        return False


def load_all() -> None:
    """Load all disk-cached figures into the in-memory store."""
    loaded = 0
    for path in sorted(CACHE_DIR.glob("*.json")):
        try:
            _store[path.stem] = pio.from_json(path.read_text(encoding="utf-8"))
            loaded += 1
        except Exception as e:
            print(f"  [figure_cache] Skipping {path.name}: {e}")
    print(f"  [figure_cache] Loaded {loaded} figures from disk.")


def get(key: str) -> go.Figure | None:
    """Return a cached figure, or None on miss."""
    return _store.get(key)


def put(key: str, fig: go.Figure) -> None:
    """Store in memory only. Use during normal runtime callbacks."""
    _store[key] = fig


def save(key: str, fig: go.Figure) -> None:
    """Store in memory and write to disk. Use during pre-warm builds."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _store[key] = fig
    (CACHE_DIR / f"{key}.json").write_text(fig.to_json(), encoding="utf-8")


def write_fingerprint() -> None:
    """Stamp the disk cache with the current DB fingerprint.
    Call once after a complete pre-warm build."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _FINGERPRINT_FILE.write_text(_current_fingerprint(), encoding="utf-8")


def clear() -> None:
    """Wipe all disk-cached figures and the in-memory store."""
    _store.clear()
    if CACHE_DIR.exists():
        for path in CACHE_DIR.glob("*.json"):
            path.unlink(missing_ok=True)
        _FINGERPRINT_FILE.unlink(missing_ok=True)


def make_key(*parts: object) -> str:
    """Build a filesystem-safe cache key from positional parts.
    Example: make_key('map', 2015, 'population', None) → 'map__2015__population__None'
    """
    return "__".join(str(p) for p in parts)
