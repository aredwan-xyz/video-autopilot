"""Stage 1 — pick a fresh, viral-leaning idea for the channel's niche."""
from __future__ import annotations

from .config import load_prompt
from .llm import complete
from .utils import extract_json, log, recent_topics


def get_trends(cfg: dict) -> list[str]:
    """Optional trend seeds. Default: none (LLM uses niche knowledge).

    Hook a real trends source here (Google Trends via pytrends, a niche RSS feed,
    YouTube search autocomplete, etc.) and return a list of keyword strings.
    The analytics feedback loop can also inject winning past topics here.
    """
    return cfg["channel"].get("trend_seeds", [])


def generate_idea(cfg: dict) -> dict:
    ch = cfg["channel"]
    trends = get_trends(cfg)
    prompt = load_prompt("ideation").format(
        niche=ch["niche"],
        name=ch["name"],
        audience=ch["audience"],
        angle=ch["angle"],
        trends="\n".join(f"- {t}" for t in trends) or "(none — use your niche expertise)",
        recent_topics="\n".join(f"- {t}" for t in recent_topics(ch["key"])) or "(none yet)",
        n=6,
    )
    data = extract_json(complete(prompt, cfg, max_tokens=1200))
    ideas = data.get("ideas", [])
    if not ideas:
        raise RuntimeError("Ideation returned no ideas.")
    best = ideas[0]  # already ranked best-first by the prompt
    log(f"idea: \"{best['title']}\" (save-worthiness {best.get('save_worthiness', '?')}/5)", "ok")
    return best
