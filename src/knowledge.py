"""Load the creator's own content data (data/) so the pipeline learns their voice + strategy.

- data/scripts/  → past scripts/captions; used as a VOICE reference for the scriptwriter.
- data/notes/    → strategy/brand/audience notes; used as guidance for ideation + scripts.

Files directly in a folder apply to all channels; files in a `<channel_key>/` subfolder apply
only to that channel. Plain .txt/.md, capped to a character budget to control token cost.
"""
from __future__ import annotations

from pathlib import Path

from .config import ROOT

DATA = ROOT / "data"


def _collect(base: Path, channel_key: str, max_chars: int) -> list:
    """Read global files in `base` plus channel-specific ones in base/<channel_key>/."""
    if not base.exists():
        return []
    files = sorted(base.glob("*.txt")) + sorted(base.glob("*.md"))
    ch_dir = base / channel_key
    if ch_dir.exists():
        files += sorted(ch_dir.glob("*.txt")) + sorted(ch_dir.glob("*.md"))

    texts, total = [], 0
    for f in files:
        try:
            t = f.read_text(encoding="utf-8").strip()
        except Exception:
            continue
        if not t:
            continue
        texts.append(t)
        total += len(t)
        if total >= max_chars:
            break
    return texts


def style_examples(channel_key: str, max_chars: int = 4000) -> str:
    """Concatenated past scripts/captions to anchor the scriptwriter's voice. '' if none."""
    texts = _collect(DATA / "scripts", channel_key, max_chars)
    joined = "\n\n---\n\n".join(texts)
    return joined[:max_chars]


def strategy_notes(channel_key: str, max_chars: int = 3000) -> str:
    """Concatenated strategy/brand notes used as guidance. '' if none."""
    texts = _collect(DATA / "notes", channel_key, max_chars)
    joined = "\n".join(texts)
    return joined[:max_chars]


def has_data() -> bool:
    for sub in ("scripts", "notes"):
        d = DATA / sub
        if d.exists() and any(d.rglob("*.txt")) or any(d.rglob("*.md")):
            return True
    return False
