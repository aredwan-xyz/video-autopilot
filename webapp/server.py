"""Web dashboard for Video Autopilot."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config"
OUTPUT = ROOT / "output"
STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Video Autopilot")


# ── job manager ──────────────────────────────────────────────────────────────
class Job:
    _ansi = re.compile(r"\x1b\[[0-9;]*m")

    def __init__(self, jid: str, label: str, channel: Optional[str] = None):
        self.id = jid
        self.label = label
        self.channel = channel
        self.status = "running"
        self.logs: list[str] = []
        self.started = datetime.now().isoformat(timespec="seconds")
        self.finished: Optional[str] = None

    def line(self, text: str) -> None:
        self.logs.append(self._ansi.sub("", text.rstrip("\n")))

    def as_dict(self, with_logs: bool = False) -> dict:
        d = {"id": self.id, "label": self.label, "channel": self.channel,
             "status": self.status, "started": self.started,
             "finished": self.finished, "log_count": len(self.logs)}
        if with_logs:
            d["logs"] = self.logs
        return d


JOBS: dict[str, Job] = {}


def _run_job(job: Job, args: list[str]) -> None:
    job.line(f"$ python -m src.orchestrator {' '.join(args)}")
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "src.orchestrator", *args],
            cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
        )
        for raw in proc.stdout:  # type: ignore[union-attr]
            job.line(raw)
        proc.wait()
        job.status = "done" if proc.returncode == 0 else "error"
        job.line(f"[exit {proc.returncode}]")
    except Exception as e:
        job.status = "error"
        job.line(f"[fatal] {e}")
    finally:
        job.finished = datetime.now().isoformat(timespec="seconds")


# ── models ───────────────────────────────────────────────────────────────────
class GenerateReq(BaseModel):
    channel: Optional[str] = None
    count: int = 1
    dry_run: bool = True
    all_channels: bool = False


class ConfigReq(BaseModel):
    content: str


# ── config ───────────────────────────────────────────────────────────────────
def _read_yaml(name: str) -> dict:
    return yaml.safe_load((CONFIG / name).read_text(encoding="utf-8")) or {}


@app.get("/api/channels")
def channels():
    data = _read_yaml("channels.yaml").get("channels", {})
    hist = {}
    hf = OUTPUT / "history.json"
    if hf.exists():
        hist = json.loads(hf.read_text(encoding="utf-8"))
    out = []
    for key, c in data.items():
        topics = hist.get(key, {}).get("topics", [])
        out.append({
            "key": key, "name": c.get("name", key), "niche": c.get("niche"),
            "tone": c.get("tone"), "audience": c.get("audience", ""),
            "angle": c.get("angle", ""), "voice": c.get("voice", ""),
            "visual_style": c.get("visual_style", ""),
            "music_mood": c.get("music_mood", ""),
            "platforms": c.get("platforms", []),
            "posts_per_day": c.get("posts_per_day", 1),
            "produced": len(topics),
            "recent_topics": topics[-5:],
        })
    return out


@app.get("/api/config/{name}")
def get_config(name: str):
    if name not in ("settings.yaml", "channels.yaml"):
        raise HTTPException(404, "unknown config file")
    return {"name": name, "content": (CONFIG / name).read_text(encoding="utf-8")}


@app.put("/api/config/{name}")
def put_config(name: str, req: ConfigReq):
    if name not in ("settings.yaml", "channels.yaml"):
        raise HTTPException(404, "unknown config file")
    try:
        yaml.safe_load(req.content)
    except yaml.YAMLError as e:
        raise HTTPException(400, f"Invalid YAML: {e}")
    (CONFIG / name).write_text(req.content, encoding="utf-8")
    return {"ok": True}


def _key_present(v) -> bool:
    """A key counts as set only if it's non-empty and not a leftover comment/placeholder."""
    if not v:
        return False
    v = v.strip()
    return bool(v) and not v.startswith("#")


@app.get("/api/env-status")
def env_status():
    from dotenv import dotenv_values
    vals = dotenv_values(ROOT / ".env")
    keys = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GROQ_API_KEY",
            "OPENROUTER_API_KEY", "GEMINI_API_KEY", "ELEVENLABS_API_KEY",
            "PEXELS_API_KEY", "FAL_KEY", "REPLICATE_API_TOKEN",
            "AYRSHARE_API_KEY", "UPLOAD_POST_API_KEY"]
    return {k: _key_present(vals.get(k)) for k in keys}


# ── generate ─────────────────────────────────────────────────────────────────
@app.post("/api/generate")
def generate(req: GenerateReq):
    args: list[str] = []
    channel = None
    if req.all_channels:
        args.append("--all")
        label = "All channels"
    elif req.channel:
        args += ["--channel", req.channel, "--count", str(req.count)]
        label = f"{req.channel} ×{req.count}"
        channel = req.channel
    else:
        raise HTTPException(400, "provide a channel or set all_channels")
    if req.dry_run:
        args.append("--dry-run")
        label += " · dry-run"

    jid = uuid.uuid4().hex[:8]
    job = Job(jid, label, channel)
    JOBS[jid] = job
    threading.Thread(target=_run_job, args=(job, args), daemon=True).start()
    return {"job_id": jid}


@app.get("/api/jobs")
def list_jobs():
    return [j.as_dict() for j in sorted(JOBS.values(), key=lambda x: x.started, reverse=True)]


@app.get("/api/jobs/{jid}")
def job_detail(jid: str):
    job = JOBS.get(jid)
    if not job:
        raise HTTPException(404, "no such job")
    return job.as_dict(with_logs=True)


# ── library ──────────────────────────────────────────────────────────────────
@app.get("/api/library")
def library():
    items = []
    for meta_file in sorted(OUTPUT.glob("*/*/*/metadata.json"), reverse=True):
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        d = meta_file.parent
        rel = d.relative_to(OUTPUT).as_posix()
        parts = rel.split("/")
        script_preview = ""
        sf = d / "script.txt"
        if sf.exists():
            script_preview = sf.read_text(encoding="utf-8")[:200]
        items.append({
            "rel": rel,
            "date": parts[0] if len(parts) > 0 else "",
            "channel": parts[1] if len(parts) > 1 else "",
            "slug": parts[2] if len(parts) > 2 else "",
            "title": (meta.get("metadata", {}).get("title")
                      or meta.get("idea", {}).get("title", rel)),
            "description": meta.get("metadata", {}).get("description", ""),
            "hashtags": meta.get("metadata", {}).get("hashtags", []),
            "status": meta.get("publish", {}).get("status", "?"),
            "has_video": (d / "final.mp4").exists(),
            "has_thumb": (d / "thumb.jpg").exists(),
            "script_preview": script_preview,
            "niche": meta.get("channel", {}).get("niche", ""),
        })
    return items[:200]


@app.get("/api/library/{rel:path}/meta")
def library_meta(rel: str):
    f = (OUTPUT / rel / "metadata.json").resolve()
    if not str(f).startswith(str(OUTPUT.resolve())) or not f.exists():
        raise HTTPException(404, "not found")
    return JSONResponse(json.loads(f.read_text(encoding="utf-8")))


@app.delete("/api/library/{rel:path}")
def library_delete(rel: str):
    d = (OUTPUT / rel).resolve()
    if not str(d).startswith(str(OUTPUT.resolve())) or not d.exists():
        raise HTTPException(404, "not found")
    shutil.rmtree(d)
    return {"ok": True}


@app.get("/api/video/{rel:path}")
def video(rel: str):
    f = (OUTPUT / rel / "final.mp4").resolve()
    if not str(f).startswith(str(OUTPUT.resolve())) or not f.exists():
        raise HTTPException(404, "not found")
    return FileResponse(f, media_type="video/mp4")


@app.get("/api/thumbnail/{rel:path}")
def thumbnail(rel: str):
    d = (OUTPUT / rel).resolve()
    if not str(d).startswith(str(OUTPUT.resolve())):
        raise HTTPException(404)
    video_path = d / "final.mp4"
    thumb = d / "thumb.jpg"
    if not video_path.exists():
        raise HTTPException(404, "no video")
    if not thumb.exists():
        proc = subprocess.run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-i", str(video_path), "-ss", "1", "-vframes", "1",
             "-vf", "scale=360:-1", str(thumb)],
            capture_output=True,
        )
        if proc.returncode != 0 or not thumb.exists():
            raise HTTPException(500, "thumb extraction failed")
    return FileResponse(thumb, media_type="image/jpeg")


# ── analytics ────────────────────────────────────────────────────────────────
@app.get("/api/analytics")
def analytics():
    hf = OUTPUT / "history.json"
    hist = json.loads(hf.read_text(encoding="utf-8")) if hf.exists() else {}
    total = sum(len(v.get("topics", [])) for v in hist.values())
    runs = []
    rf = OUTPUT / "runs.jsonl"
    if rf.exists():
        for ln in rf.read_text(encoding="utf-8").splitlines()[-100:]:
            try:
                runs.append(json.loads(ln))
            except Exception:
                pass
    return {
        "total_videos": total,
        "channels": {k: len(v.get("topics", [])) for k, v in hist.items()},
        "recent_runs": list(reversed(runs)),
    }


# ── static ───────────────────────────────────────────────────────────────────
app.mount("/", StaticFiles(directory=str(STATIC), html=True), name="static")
