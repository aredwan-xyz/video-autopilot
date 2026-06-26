"""Stage 3 — synthesize the voiceover. edge-tts (free) or ElevenLabs (premium)."""
from __future__ import annotations

import asyncio
from pathlib import Path

from .config import env
from .utils import ffprobe_duration, log, run_ffmpeg


def synthesize(cfg: dict, text: str, out_dir: Path) -> Path:
    raw = out_dir / "voice_raw.mp3"
    final = out_dir / "voice.mp3"
    provider = cfg["tts"]["provider"]

    if provider == "edge":
        _edge_tts(cfg, text, raw)
    elif provider == "elevenlabs":
        _elevenlabs(cfg, text, raw)
    else:
        raise ValueError(f"Unknown tts.provider: {provider}")

    # Normalize loudness + apply energetic speed-up (atempo) for retention.
    speed = cfg["tts"].get("speed", 1.0)
    run_ffmpeg([
        "-i", str(raw),
        "-filter:a", f"atempo={speed},loudnorm=I=-16:TP=-1.5:LRA=11",
        "-ar", "44100", str(final),
    ])
    dur = ffprobe_duration(final)
    log(f"voiceover: voice.mp3 ({dur:.1f}s, {provider})", "ok")
    return final


def _edge_tts(cfg: dict, text: str, out: Path) -> None:
    import edge_tts

    voice = cfg["tts"].get("edge_voice", "en-US-AriaNeural")

    async def _run():
        await edge_tts.Communicate(text, voice).save(str(out))

    asyncio.run(_run())


def _elevenlabs(cfg: dict, text: str, out: Path) -> None:
    import requests

    key = env("ELEVENLABS_API_KEY")
    if not key:
        raise SystemExit("ELEVENLABS_API_KEY missing in .env")
    voice = cfg["tts"].get("elevenlabs_voice", "Rachel")
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",
        headers={"xi-api-key": key, "Content-Type": "application/json"},
        json={
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": cfg["tts"].get("elevenlabs_stability", 0.4),
                "similarity_boost": 0.75,
            },
        },
        timeout=120,
    )
    r.raise_for_status()
    out.write_bytes(r.content)
