"""Shared helpers: logging, slugs, JSON parsing, run directories, history, ffprobe."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

from .config import ROOT

HISTORY_FILE = ROOT / "output" / "history.json"

_ICONS = {"info": "•", "ok": "✓", "warn": "!", "err": "✗", "step": "▶"}


def log(msg: str, kind: str = "info") -> None:
    print(f"  {_ICONS.get(kind, '•')} {msg}", flush=True)


def banner(msg: str) -> None:
    print(f"\n\033[1m{msg}\033[0m", flush=True)


def die(msg: str) -> None:
    print(f"\033[31m✗ {msg}\033[0m", file=sys.stderr)
    raise SystemExit(1)


def slugify(text: str, max_len: int = 50) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:max_len].strip("-") or "video"


def extract_json(text: str) -> dict:
    """Pull the first JSON object out of an LLM response (handles ```json fences)."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in model output:\n{text[:500]}")
    return json.loads(text[start : end + 1])


def run_dir(output_dir: str, channel_key: str, slug: str) -> Path:
    d = ROOT / output_dir / date.today().isoformat() / channel_key / slug
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def ffprobe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def run_ffmpeg(args: list[str]) -> None:
    """Run ffmpeg quietly; raise with stderr tail on failure."""
    proc = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{proc.stderr[-1500:]}")


# ── topic history (avoid repeats + power the feedback loop) ──
def load_history() -> dict:
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    return {}


def recent_topics(channel_key: str, limit: int = 40) -> list[str]:
    return load_history().get(channel_key, {}).get("topics", [])[-limit:]


def record_topic(channel_key: str, title: str) -> None:
    h = load_history()
    h.setdefault(channel_key, {}).setdefault("topics", []).append(title)
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(h, indent=2, ensure_ascii=False), encoding="utf-8")
