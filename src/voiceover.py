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

    # ── Broadcast voice-mastering chain (free, all in ffmpeg) ──
    # speed-up → de-rumble → compress for consistent level → presence EQ →
    # tame harsh sibilance → normalize to -16 LUFS (leaves headroom for music;
    # the final mix is brought to platform -14 LUFS in assemble.py).
    speed = cfg["tts"].get("speed", 1.0)
    chain = (
        f"atempo={speed},"
        "highpass=f=85,"                                  # cut low rumble/hum
        "acompressor=threshold=-20dB:ratio=3.5:attack=5:release=140:makeup=3,"  # even, punchy level
        "equalizer=f=180:t=q:w=1.0:g=-2,"                 # de-mud the low-mids
        "equalizer=f=3200:t=q:w=1.6:g=3,"                 # presence/intelligibility lift
        "treble=g=2:f=9000,"                              # subtle air
        "deesser=i=0.35,"                                 # reduce harsh "s" sounds
        "loudnorm=I=-16:TP=-1.5:LRA=11,"
        "alimiter=limit=0.95"                             # safety ceiling, no clipping
    )
    run_ffmpeg([
        "-i", str(raw),
        "-filter:a", chain,
        "-ar", "48000", str(final),
    ])
    dur = ffprobe_duration(final)
    log(f"voiceover: voice.mp3 ({dur:.1f}s, {provider}, mastered)", "ok")
    return final


def _edge_tts(cfg: dict, text: str, out: Path) -> None:
    import edge_tts

    voice = cfg["tts"].get("edge_voice", "en-US-AriaNeural")
    rate = cfg["tts"].get("edge_rate", "+0%")     # e.g. "+8%" for more energy
    pitch = cfg["tts"].get("edge_pitch", "+0Hz")  # e.g. "+2Hz" for warmth

    async def _run():
        await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(str(out))

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
