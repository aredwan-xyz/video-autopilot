"""The daily pipeline — runs all 9 stages for one or more videos on a channel.

Usage:
  python -m src.orchestrator --channel motivation --count 1 --dry-run
  python -m src.orchestrator --channel money               # uses settings.yaml publish provider
  python -m src.orchestrator --all                         # every channel, posts_per_day each
  python -m src.orchestrator --report                      # analytics feedback report
"""
from __future__ import annotations

import argparse
import traceback

from . import analytics
from .assemble import assemble
from .captions import build_captions
from .config import all_channel_keys, channel_config
from .ideation import generate_idea
from .metadata import build_metadata
from .publish import publish
from .scriptwriter import write_script
from .utils import (banner, ffprobe_duration, log, record_topic, run_dir,
                    save_json, slugify)
from .visuals import gather_visuals
from .voiceover import synthesize


def make_one(cfg: dict) -> dict:
    ch = cfg["channel"]
    banner(f"🎬 {ch['name']} ({ch['key']}) — building 1 video")

    idea = generate_idea(cfg)                                    # 1
    script = write_script(cfg, idea)                             # 2
    slug = slugify(idea["title"])
    out = run_dir(cfg["output_dir"], ch["key"], slug)

    (out / "script.txt").write_text(script["full_script"], encoding="utf-8")
    voice = synthesize(cfg, script["full_script"], out)         # 3
    dur = ffprobe_duration(voice)
    clips = gather_visuals(cfg, script, out, dur)               # 4
    captions = build_captions(cfg, voice, out)                  # 5
    video = assemble(cfg, clips, voice, captions, out)          # 6
    meta = build_metadata(cfg, script)                          # 7
    result = publish(cfg, video, meta)                          # 8

    save_json(out / "metadata.json", {
        "idea": idea, "script": script, "metadata": meta, "publish": result,
        "video": str(video),
    })
    record_topic(ch["key"], idea["title"])                      # history (anti-repeat)
    analytics.record_run(ch["key"], slug, meta, result)         # 9 feedback log
    log(f"done → {out}", "ok")
    return {"slug": slug, "out": str(out), "result": result}


def run_channel(channel_key: str, count: int, dry_run: bool) -> None:
    cfg = channel_config(channel_key)
    if dry_run:
        cfg["publish"]["provider"] = "dry_run"
    for i in range(count):
        if count > 1:
            banner(f"── video {i + 1} of {count} ──")
        try:
            make_one(cfg)
        except Exception as e:
            log(f"FAILED video {i + 1}: {e}", "err")
            traceback.print_exc()


def main() -> None:
    p = argparse.ArgumentParser(description="Video Autopilot pipeline")
    p.add_argument("--channel", help="channel key from config/channels.yaml")
    p.add_argument("--count", type=int, default=1, help="videos to make this run")
    p.add_argument("--all", action="store_true", help="run every channel (posts_per_day each)")
    p.add_argument("--dry-run", action="store_true", help="build locally, do not post")
    p.add_argument("--report", action="store_true", help="print analytics report and exit")
    args = p.parse_args()

    if args.report:
        analytics.report(args.channel)
        return

    if args.all:
        for key in all_channel_keys():
            cfg = channel_config(key)
            run_channel(key, cfg["channel"].get("posts_per_day", 1), args.dry_run)
    elif args.channel:
        run_channel(args.channel, args.count, args.dry_run)
    else:
        p.error("provide --channel <key>, or --all, or --report")


if __name__ == "__main__":
    main()
