"""Stage 9 — the feedback loop.

Pull performance for past posts and surface the winning hooks/topics so ideation can bias
toward what's working (Playbook §6 flywheel). This reads the local run log; wire a platform
analytics API (or Ayrshare /analytics) into `_fetch_stats` to make it live.
"""
from __future__ import annotations

import json

from .config import ROOT
from .utils import banner, load_history

RUNS_LOG = ROOT / "output" / "runs.jsonl"


def record_run(channel_key: str, slug: str, meta: dict, result: dict) -> None:
    RUNS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(RUNS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "channel": channel_key, "slug": slug,
            "title": meta.get("title"), "status": result.get("status"),
        }) + "\n")


def _fetch_stats(channel_key: str) -> list[dict]:
    """Stub: return [{title, views, retention, saves}, ...]. Hook your analytics API here."""
    return []


def report(channel_key: str | None = None) -> None:
    banner("📊 Performance report")
    hist = load_history()
    keys = [channel_key] if channel_key else list(hist.keys())
    if not keys:
        print("  No runs recorded yet. Generate some videos first.")
        return
    for k in keys:
        topics = hist.get(k, {}).get("topics", [])
        print(f"\n  {k}: {len(topics)} videos produced")
        stats = _fetch_stats(k)
        if stats:
            top = sorted(stats, key=lambda s: s.get("views", 0), reverse=True)[:3]
            for s in top:
                print(f"    ★ {s['views']:>8,} views — {s['title']}")
            print("    → feed these winning angles back into config/prompts/ideation.md")
        else:
            print("    (no live stats — connect an analytics API in analytics._fetch_stats)")
