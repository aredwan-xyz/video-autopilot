"""Stage 6 — composite everything into a clean 9:16 master with ffmpeg.

clips → normalized 1080x1920 segments → concat → + voiceover + ducked music
→ burn captions → optional progress bar. One watermark-free master for all platforms.
"""
from __future__ import annotations

import random
from pathlib import Path

from .config import ROOT
from .utils import ffprobe_duration, log, run_ffmpeg

MUSIC_DIR = ROOT / "assets" / "music"
W, H = 1080, 1920


def _normalize_segment(src: Path, dest: Path, seconds: float, fps: int) -> None:
    """Scale+crop any image/video to a fixed-length 9:16 segment with subtle zoom."""
    is_image = src.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},"
        # gentle Ken Burns / motion so static frames still move (retention)
        f"zoompan=z='min(zoom+0.0008,1.12)':d={int(seconds*fps)}:s={W}x{H}:fps={fps},"
        f"setsar=1"
    )
    if is_image:
        args = ["-loop", "1", "-t", f"{seconds}", "-i", str(src),
                "-vf", vf, "-r", str(fps), "-pix_fmt", "yuv420p", "-an", str(dest)]
    else:
        # take a random window of the source clip for variety, loop if too short
        args = ["-stream_loop", "-1", "-t", f"{seconds}", "-i", str(src),
                "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1",
                "-r", str(fps), "-pix_fmt", "yuv420p", "-an", str(dest)]
    run_ffmpeg(args)


def assemble(cfg: dict, clips: list[Path], voice: Path, captions: Path | None,
            out_dir: Path) -> Path:
    fps = cfg["video"]["fps"]
    cut = cfg["video"]["cut_every_seconds"]
    voice_dur = ffprobe_duration(voice)
    total = voice_dur + 0.6  # small tail so audio doesn't clip
    seg_dir = out_dir / "segments"
    seg_dir.mkdir(exist_ok=True)

    # Build enough normalized segments to cover the voiceover.
    n_segments = max(1, int(total // cut) + 1)
    segments = []
    for i in range(n_segments):
        src = clips[i % len(clips)]
        dest = seg_dir / f"seg{i:02d}.mp4"
        _normalize_segment(src, dest, cut, fps)
        segments.append(dest)

    # Concat the silent video track.
    concat_list = seg_dir / "list.txt"
    concat_list.write_text("".join(f"file '{s.name}'\n" for s in segments), encoding="utf-8")
    silent = out_dir / "silent.mp4"
    run_ffmpeg(["-f", "concat", "-safe", "0", "-i", str(concat_list),
                "-t", f"{total}", "-c", "copy", str(silent)])

    # Audio mix: voiceover + ducked background music (if any track present).
    music = _pick_music()
    mixed = out_dir / "mixed_audio.m4a"
    music_vol = cfg["video"]["music_volume_db"]
    if music:
        run_ffmpeg([
            "-i", str(voice), "-stream_loop", "-1", "-i", str(music),
            "-filter_complex",
            f"[1:a]volume={music_vol}dB[m];[0:a][m]amix=inputs=2:duration=first:dropout_transition=0[a]",
            "-map", "[a]", "-t", f"{total}", "-c:a", "aac", "-b:a", "192k", str(mixed),
        ])
        audio = mixed
    else:
        audio = voice

    # Final mux + burn captions + optional progress bar.
    final = out_dir / "final.mp4"
    vf_filters = []
    if captions and captions.exists():
        font_dir = (ROOT / "assets" / "fonts").as_posix()
        ass = captions.as_posix().replace(":", r"\:")
        vf_filters.append(f"subtitles='{ass}':fontsdir='{font_dir}'")
    if cfg["video"].get("add_progress_bar"):
        vf_filters.append(
            f"drawbox=x=0:y=ih-8:w='iw*t/{total:.2f}':h=8:color=white@0.85:t=fill"
        )
    vf = ",".join(vf_filters) if vf_filters else "null"

    run_ffmpeg([
        "-i", str(silent), "-i", str(audio),
        "-vf", vf,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", str(fps),
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{total}", "-movflags", "+faststart", str(final),
    ])
    log(f"assemble: final.mp4 ({W}x{H}, {ffprobe_duration(final):.1f}s)", "ok")
    return final


def _pick_music() -> Path | None:
    tracks = [p for p in MUSIC_DIR.glob("*") if p.suffix.lower() in (".mp3", ".m4a", ".wav")]
    return random.choice(tracks) if tracks else None
