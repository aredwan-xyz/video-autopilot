"""Stage 5 — word-level captions via faster-whisper → styled ASS subtitle file.

Word-by-word burned-in captions are the single biggest free retention lever for muted
viewing (Playbook §2). We transcribe the actual voiceover so timing is frame-accurate.
"""
from __future__ import annotations

from pathlib import Path

from .utils import log


def _ts(seconds: float) -> str:
    cs = int(round(seconds * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def build_captions(cfg: dict, voice_path: Path, out_dir: Path) -> Path | None:
    if not cfg["captions"].get("enabled", True):
        return None
    from faster_whisper import WhisperModel

    style = cfg["captions"]["style"]
    model = WhisperModel(cfg["captions"].get("model", "base"), compute_type="int8")
    segments, _ = model.transcribe(str(voice_path), word_timestamps=True)

    # Flatten to words.
    words = []
    for seg in segments:
        for w in (seg.words or []):
            token = w.word.strip()
            if token:
                words.append((token, w.start, w.end))
    if not words:
        log("captions: no words detected; skipping", "warn")
        return None

    max_words = style.get("max_words_per_cue", 3)
    uppercase = style.get("uppercase", True)
    res_x, res_y = cfg["video"]["width"], cfg["video"]["height"]
    align = {"top": 8, "middle": 5, "bottom": 2}.get(style.get("position", "middle"), 5)

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {res_x}
PlayResY: {res_y}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Base,Montserrat,{style['font_size']},{style['primary_color']},&H00000000,&H64000000,1,{style['outline']},{style['shadow']},{align},80,80,{cfg['video']['safe_zone_padding']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    lines = []
    highlight = style.get("highlight_color", "&H0000F2FF")
    # Group words into small cues; within a cue, highlight the active word.
    for i in range(0, len(words), max_words):
        group = words[i : i + max_words]
        g_start, g_end = group[0][1], group[-1][2]
        for j, (tok, w_start, w_end) in enumerate(group):
            parts = []
            for k, (t2, _, _) in enumerate(group):
                disp = t2.upper() if uppercase else t2
                if k == j:
                    parts.append(f"{{\\c{highlight}}}{disp}{{\\c{style['primary_color']}}}")
                else:
                    parts.append(disp)
            text = " ".join(parts)
            start = w_start if j > 0 else g_start
            end = w_end if j < len(group) - 1 else g_end
            lines.append(
                f"Dialogue: 0,{_ts(start)},{_ts(end)},Base,,0,0,0,,{text}"
            )

    ass_path = out_dir / "captions.ass"
    ass_path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
    log(f"captions: captions.ass ({len(words)} words)", "ok")
    return ass_path
