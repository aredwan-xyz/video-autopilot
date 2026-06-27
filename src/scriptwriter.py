"""Stage 2 — turn an idea into a tight, retention-optimized voiceover script."""
from __future__ import annotations

import json

from .config import load_prompt
from .llm import complete
from .utils import extract_json, log


def write_script(cfg: dict, idea: dict) -> dict:
    ch = cfg["channel"]
    target = cfg["video"]["target_seconds"]
    word_budget = int(target * 2.4)      # ~2.4 spoken words/sec — lower bound
    word_budget_max = int(target * 3.0)  # upper bound for a brisk read

    disclaimer_line = ""
    dkey = ch.get("inject_disclaimer")
    if dkey:
        text = cfg["compliance"]["disclaimers"].get(dkey, "")
        if text:
            disclaimer_line = f'- End the script with this exact disclaimer: "{text}"'

    prompt = load_prompt("script").format(
        niche=ch["niche"], name=ch["name"], tone=ch["tone"], audience=ch["audience"],
        title=idea["title"], concept=idea["concept"], hook_angle=idea.get("hook_angle", ""),
        primary_keyword=idea.get("primary_keyword", idea["title"]),
        search_question=idea.get("search_question", ""),
        target_seconds=target, word_budget=word_budget, word_budget_max=word_budget_max,
        disclaimer_line=disclaimer_line,
    )

    script = extract_json(complete(prompt, cfg, max_tokens=1500))
    if not script.get("full_script"):
        raise RuntimeError("Scriptwriter returned no full_script.")

    # Small free models tend to under-write. Expand the draft toward the budget
    # (models hit a target far better when expanding existing text than writing cold).
    min_words = int(word_budget * 0.85)
    for _ in range(2):
        wc = len(script["full_script"].split())
        if wc >= min_words:
            break
        log(f"script short ({wc}w) — expanding toward {word_budget}w", "warn")
        expand = (
            f"This voiceover script is too short at {wc} words. Rewrite it to be "
            f"{word_budget}-{word_budget_max} words by deepening each beat with concrete, "
            f"vivid detail and complete spoken sentences. Keep the hook and the punchy tone. "
            f"Return the SAME JSON shape.\n\nCurrent script JSON:\n{json.dumps(script)}"
        )
        expanded = extract_json(complete(expand, cfg, max_tokens=1500))
        if expanded.get("full_script"):
            script = expanded

    wc = len(script["full_script"].split())
    log(f"script: hook + {len(script.get('beats', []))} beats, {wc} words", "ok")
    return script
