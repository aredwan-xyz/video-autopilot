"""Stage 6 — composite everything into a clean, cinematic 9:16 master with ffmpeg.

clips → normalized 1080x1920 segments with alternating Ken Burns motion → concat
→ + mastered voiceover + ducked music → color grade + vignette → burn animated captions
+ hook title → progress bar → platform -14 LUFS. One watermark-free master for all platforms.
"""
from __future__ import annotations

import random
from pathlib import Path
from typing import Optional

from .config import ROOT
from .utils import ffprobe_duration, log, run_ffmpeg

MUSIC_DIR = ROOT / "assets" / "music"
W, H = 1080, 1920


def _normalize_segment(src: Path, dest: Path, seconds: float, fps: int, idx: int) -> None:
    """Scale+crop any image/video to a fixed-length 9:16 segment.

    Images get alternating Ken Burns motion (zoom-in vs zoom-out + drift) so static frames
    feel alive and consecutive cuts don't move the same way — a subtle pro touch.
    """
    is_image = src.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
    frames = max(1, int(seconds * fps))
    if is_image:
        if idx % 2 == 0:
            # slow zoom IN with a gentle rightward drift
            z = "min(zoom+0.0009,1.18)"
            x = "iw/2-(iw/zoom/2)+(on/{d})*40".format(d=frames)
            y = "ih/2-(ih/zoom/2)"
        else:
            # start zoomed, ease OUT with a gentle leftward drift
            z = "if(eq(on,0),1.18,max(zoom-0.0009,1.02))"
            x = "iw/2-(iw/zoom/2)-(on/{d})*40".format(d=frames)
            y = "ih/2-(ih/zoom/2)"
        vf = (
            f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
            f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={fps},setsar=1"
        )
        args = ["-loop", "1", "-t", f"{seconds}", "-i", str(src),
                "-vf", vf, "-r", str(fps), "-pix_fmt", "yuv420p", "-an", str(dest)]
    else:
        # real footage already moves; just fit it cleanly to 9:16
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"
        args = ["-stream_loop", "-1", "-t", f"{seconds}", "-i", str(src),
                "-vf", vf, "-r", str(fps), "-pix_fmt", "yuv420p", "-an", str(dest)]
    run_ffmpeg(args)


def assemble(cfg: dict, clips: list, voice: Path, captions: Optional[Path],
             out_dir: Path) -> Path:
    vcfg = cfg["video"]
    fps = vcfg["fps"]
    cut = vcfg["cut_every_seconds"]
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
        _normalize_segment(src, dest, cut, fps, i)
        segments.append(dest)

    # Concat the silent video track.
    concat_list = seg_dir / "list.txt"
    concat_list.write_text("".join(f"file '{s.name}'\n" for s in segments), encoding="utf-8")
    silent = out_dir / "silent.mp4"
    run_ffmpeg(["-f", "concat", "-safe", "0", "-i", str(concat_list),
                "-t", f"{total}", "-c", "copy", str(silent)])

    # Audio mix: mastered voiceover + ducked background music (if any track present).
    music = _pick_music()
    mixed = out_dir / "mixed_audio.m4a"
    music_vol = vcfg["music_volume_db"]
    if music:
        # sidechain-duck the music under the voice so narration always stays clear.
        run_ffmpeg([
            "-i", str(voice), "-stream_loop", "-1", "-i", str(music),
            "-filter_complex",
            f"[1:a]volume={music_vol}dB[mv];"
            f"[mv][0:a]sidechaincompress=threshold=0.03:ratio=8:attack=5:release=300[mduck];"
            f"[0:a][mduck]amix=inputs=2:duration=first:dropout_transition=0,"
            f"loudnorm=I=-14:TP=-1.0:LRA=11[a]",
            "-map", "[a]", "-t", f"{total}", "-c:a", "aac", "-b:a", "256k", str(mixed),
        ])
        audio = mixed
    else:
        # no music: still bring the final voice to platform loudness.
        run_ffmpeg([
            "-i", str(voice), "-filter:a", "loudnorm=I=-14:TP=-1.0:LRA=11",
            "-t", f"{total}", "-c:a", "aac", "-b:a", "256k", str(mixed),
        ])
        audio = mixed

    # ── Final video filter chain: grade → vignette → captions → progress bar ──
    vf_filters = []
    if vcfg.get("color_grade", True):
        # cinematic punch: contrast, saturation, micro-lift, gentle sharpen
        vf_filters.append("eq=contrast=1.07:saturation=1.14:brightness=0.012:gamma=0.98")
        vf_filters.append("unsharp=5:5:0.5:5:5:0.0")
        vf_filters.append("vignette=PI/4.5")
    if captions and captions.exists():
        font_dir = (ROOT / "assets" / "fonts").as_posix()
        ass = captions.as_posix().replace(":", r"\:")
        vf_filters.append(f"subtitles='{ass}':fontsdir='{font_dir}'")
    if vcfg.get("add_progress_bar"):
        bar = vcfg.get("progress_bar_color", "0x06D6A0")  # accent, not plain white
        vf_filters.append(
            f"drawbox=x=0:y=ih-10:w='iw*t/{total:.2f}':h=10:color={bar}@0.9:t=fill"
        )
    vf = ",".join(vf_filters) if vf_filters else "null"

    final = out_dir / "final.mp4"
    run_ffmpeg([
        "-i", str(silent), "-i", str(audio),
        "-vf", vf,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", vcfg.get("encode_preset", "slow"),
        "-crf", str(vcfg.get("crf", 19)),
        "-pix_fmt", "yuv420p", "-r", str(fps),
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
        "-t", f"{total}", "-movflags", "+faststart", str(final),
    ])
    log(f"assemble: final.mp4 ({W}x{H}, {ffprobe_duration(final):.1f}s, graded)", "ok")
    return final


def _pick_music() -> Optional[Path]:
    tracks = [p for p in MUSIC_DIR.glob("*") if p.suffix.lower() in (".mp3", ".m4a", ".wav")]
    return random.choice(tracks) if tracks else None
