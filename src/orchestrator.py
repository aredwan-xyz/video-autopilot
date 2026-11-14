"""The daily pipeline — runs all 9 stages for one or more videos on a channel.

Usage:
  python -m src.orchestrator --channel motivation --count 1 --dry-run
  python -m src.orchestrator --channel money               # uses settings.yaml publish provider
  python -m src.orchestrator --all                         # every channel, posts_per_day each
  python -m src.orchestrator --report                      # analytics feedback report
"""
from __future__ import annotations

import argparse
import json
import traceback
from pathlib import Path

from . import analytics
from .assemble import assemble
from .captions import build_captions
from .config import ROOT, all_channel_keys, channel_config
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
    captions = build_captions(cfg, voice, out,                  # 5
                              hook_title=script.get("on_screen_title", ""))
    video = assemble(cfg, clips, voice, captions, out)          # 6
    if not video.is_file() or video.stat().st_size == 0 or ffprobe_duration(video) <= 0:
        raise RuntimeError("Assembly did not produce a non-empty, playable video")
    meta = build_metadata(cfg, script, idea)                    # 7
    result = publish(cfg, video, meta)                          # 8

    save_json(out / "metadata.json", {
        "idea": idea, "script": script, "metadata": meta, "publish": result,
        "video": str(video),
    })
    if result.get("status") not in {"dry_run", "queued", "submitted", "posted"}:
        raise RuntimeError(f"Publishing incomplete: {result.get('status', 'unknown')}")
    record_topic(ch["key"], idea["title"])                      # history (anti-repeat)
    analytics.record_run(ch["key"], slug, meta, result)         # 9 feedback log
    log(f"done → {out}", "ok")
    return {"slug": slug, "out": str(out), "video": str(video),
            "metadata": str(out / "metadata.json"), "result": result}


def run_channel(channel_key: str, count: int, dry_run: bool) -> list[dict]:
    if count < 1:
        raise ValueError("Video count must be positive")
    cfg = channel_config(channel_key)
    if dry_run:
        cfg["publish"]["provider"] = "dry_run"
    outcomes = []
    for i in range(count):
        if count > 1:
            banner(f"── video {i + 1} of {count} ──")
        try:
            item = make_one(cfg)
            if item.get("result", {}).get("status") not in {"dry_run", "queued", "submitted", "posted"}:
                raise RuntimeError("Publishing did not complete its requested mode")
            for key in ("video", "metadata"):
                artifact = Path(item[key])
                if not artifact.is_file() or artifact.stat().st_size == 0:
                    raise RuntimeError(f"Missing or empty {key} artifact")
            outcomes.append({"channel": channel_key, "ok": True, **item})
        except (Exception, SystemExit) as e:
            log(f"FAILED video {i + 1}: {e}", "err")
            traceback.print_exc()
            outcomes.append({"channel": channel_key, "ok": False,
                             "attempt": i + 1, "error_type": type(e).__name__})
    return outcomes


def verify_manifest(path: Path) -> bool:
    """Only artifacts from this invocation count toward completion."""
    manifest = json.loads(path.read_text(encoding="utf-8"))
    outcomes = manifest.get("outcomes", [])
    if (manifest.get("status") != "complete" or manifest.get("expected", 0) < 1
            or len(outcomes) != manifest["expected"]):
        return False
    videos = [item.get("video") for item in outcomes]
    if len(set(videos)) != len(videos):
        return False
    for item in outcomes:
        if not item.get("ok") or item.get("result", {}).get("status") not in {
            "dry_run", "queued", "submitted", "posted"
        }:
            return False
        for key in ("video", "metadata"):
            artifact = Path(item.get(key, ""))
            if not artifact.is_file() or artifact.stat().st_size == 0:
                return False
    return True


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Video Autopilot pipeline")
    p.add_argument("--channel", help="channel key from config/channels.yaml")
    p.add_argument("--count", type=int, default=1, help="videos to make this run")
    p.add_argument("--all", action="store_true", help="run every channel (posts_per_day each)")
    p.add_argument("--dry-run", action="store_true", help="build locally, do not post")
    p.add_argument("--report", action="store_true", help="print analytics report and exit")
    p.add_argument("--manifest", type=Path, default=ROOT / "output" / "run-manifest.json")
    p.add_argument("--verify-manifest", action="store_true", help="Check this run's required artifacts")
    args = p.parse_args(argv)
    if args.verify_manifest:
        return 0 if verify_manifest(args.manifest) else 1

    if args.report:
        analytics.report(args.channel)
        return 0

    outcomes = []
    expected = 0
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    save_json(args.manifest, {"status": "started", "expected": 0, "outcomes": []})
    if args.all:
        for key in all_channel_keys():
            cfg = channel_config(key)
            count = cfg["channel"].get("posts_per_day", 1)
            expected += count
            outcomes.extend(run_channel(key, count, args.dry_run))
    elif args.channel:
        expected = args.count
        outcomes = run_channel(args.channel, args.count, args.dry_run)
    else:
        p.error("provide --channel <key>, or --all, or --report")
    complete = expected > 0 and len(outcomes) == expected and all(x["ok"] for x in outcomes)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    save_json(args.manifest, {"status": "complete" if complete else "failed",
                              "expected": expected, "succeeded": sum(x["ok"] for x in outcomes),
                              "outcomes": outcomes})
    if complete and verify_manifest(args.manifest):
        return 0
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    manifest["status"] = "failed"
    save_json(args.manifest, manifest)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
