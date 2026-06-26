"""Stage 8 — publish the master to all platforms.

Direct YouTube/TikTok/Meta APIs each need their own OAuth + review; for true autopilot we
default to an aggregator (Ayrshare / upload-post) that fans one upload out to all four with a
single token. `dry_run` validates the pipeline without posting.
"""
from __future__ import annotations

import time
from pathlib import Path

from .config import env
from .utils import log


def publish(cfg: dict, video: Path, meta: dict) -> dict:
    provider = cfg["publish"]["provider"]
    platforms = cfg["publish"]["platforms"]
    caption = _caption(meta)

    if cfg["publish"].get("queue"):
        log(f"publish: QUEUED for review (not posted) → {', '.join(platforms)}", "warn")
        return {"status": "queued", "platforms": platforms}

    if provider == "dry_run":
        log(f"publish: [DRY-RUN] would post to {', '.join(platforms)}", "warn")
        log(f"          title: {meta.get('title')}", "info")
        return {"status": "dry_run", "platforms": platforms, "caption": caption}
    if provider == "ayrshare":
        return _ayrshare(cfg, video, meta, caption, platforms)
    if provider == "upload_post":
        return _upload_post(cfg, video, meta, caption, platforms)
    raise ValueError(f"Unknown publish.provider: {provider}")


def _caption(meta: dict) -> str:
    tags = " ".join(meta.get("hashtags", []))
    return f"{meta.get('description', meta.get('title',''))}\n\n{tags}".strip()


def _ayrshare(cfg, video, meta, caption, platforms) -> dict:
    import requests

    key = env("AYRSHARE_API_KEY")
    if not key:
        raise SystemExit("AYRSHARE_API_KEY missing in .env")

    # Ayrshare needs a public URL; upload to its media endpoint first.
    up = requests.post(
        "https://api.ayrshare.com/api/media/upload",
        headers={"Authorization": f"Bearer {key}"},
        files={"file": open(video, "rb")}, timeout=300,
    )
    up.raise_for_status()
    media_url = up.json().get("url") or up.json().get("mediaUrl")

    results = {}
    for i, platform in enumerate(platforms):
        if i:
            time.sleep(cfg["publish"].get("stagger_seconds", 0))
        payload = {
            "post": caption,
            "platforms": [platform],
            "mediaUrls": [media_url],
            "isVideo": True,
        }
        if platform == "youtube":
            payload["youTubeOptions"] = {"title": meta["title"][:100], "shorts": True}
        if cfg["compliance"].get("ai_disclosure"):
            payload.setdefault("tikTokOptions", {})["aiGenerated"] = True
        r = requests.post(
            "https://api.ayrshare.com/api/post",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json=payload, timeout=120,
        )
        ok = r.status_code < 300
        results[platform] = "posted" if ok else f"error {r.status_code}: {r.text[:200]}"
        log(f"publish→{platform}: {results[platform]}", "ok" if ok else "err")
    return {"status": "posted", "results": results}


def _upload_post(cfg, video, meta, caption, platforms) -> dict:
    import requests

    key = env("UPLOAD_POST_API_KEY")
    user = env("UPLOAD_POST_USER")
    if not key:
        raise SystemExit("UPLOAD_POST_API_KEY missing in .env")
    r = requests.post(
        "https://api.upload-post.com/api/upload",
        headers={"Authorization": f"Apikey {key}"},
        data={"user": user, "title": meta["title"][:100],
              "caption": caption, "platform[]": platforms},
        files={"video": open(video, "rb")}, timeout=300,
    )
    ok = r.status_code < 300
    log(f"publish: upload-post {'ok' if ok else 'error'} ({r.status_code})", "ok" if ok else "err")
    return {"status": "posted" if ok else "error", "response": r.text[:300]}
