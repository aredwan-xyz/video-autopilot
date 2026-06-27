"""Stage 7 — SEO titles, description, hashtags, pinned comment, thumbnail text."""
from __future__ import annotations

from typing import Optional

from .config import load_prompt
from .llm import complete
from .utils import extract_json, log


def build_metadata(cfg: dict, script: dict, idea: Optional[dict] = None) -> dict:
    ch = cfg["channel"]
    idea = idea or {}
    prompt = load_prompt("metadata").format(
        niche=ch["niche"], name=ch["name"], full_script=script["full_script"],
        primary_keyword=idea.get("primary_keyword", idea.get("title", ch["niche"])),
        search_question=idea.get("search_question", ""),
        title_variants=cfg["metadata"]["title_variants"],
        hashtags_per_post=cfg["metadata"]["hashtags_per_post"],
    )
    meta = extract_json(complete(prompt, cfg, max_tokens=800))

    # Append compliance lines to the description.
    extra = []
    dkey = ch.get("inject_disclaimer")
    if dkey:
        extra.append(cfg["compliance"]["disclaimers"].get(dkey, ""))
    if cfg["compliance"].get("ai_disclosure"):
        extra.append("Created with AI assistance.")
    if extra:
        meta["description"] = meta.get("description", "") + "\n\n" + " ".join(filter(None, extra))

    meta["title"] = meta.get("titles", ["Untitled"])[0]
    log(f"metadata: \"{meta['title']}\" + {len(meta.get('hashtags', []))} tags", "ok")
    return meta
