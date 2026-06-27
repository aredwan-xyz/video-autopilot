"""Stage 5 — word-level animated captions via faster-whisper → styled ASS.

Kinetic, word-by-word burned-in captions are the single biggest free retention lever for
muted viewing (Playbook §2). We transcribe the actual voiceover so timing is frame-accurate,
then animate the active word with a scale "pop" + color highlight for that pro, viral look.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from .utils import log

# Strip markdown / stray formatting an LLM might leave in on-screen text.
_MD = re.compile(r"[*_`#~]+")


def _clean(text: str) -> str:
    return _MD.sub("", text).strip().strip('"').strip("'").strip()


def _ts(seconds: float) -> str:
    cs = int(round(seconds * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def build_captions(cfg: dict, voice_path: Path, out_dir: Path,
                   hook_title: str = "") -> Optional[Path]:
    if not cfg["captions"].get("enabled", True):
        return None
    from faster_whisper import WhisperModel

    style = cfg["captions"]["style"]
    model = WhisperModel(cfg["captions"].get("model", "base"), compute_type="int8")
    segments, _ = model.transcribe(str(voice_path), word_timestamps=True)

    # Flatten to words with timings.
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
    primary = style["primary_color"]
    highlight = style.get("highlight_color", "&H0000F2FF")
    outline_col = style.get("outline_color", "&H00000000")
    fontname = style.get("fontname", "Montserrat")

    # Style: heavy outline + soft shadow = legible on ANY background. Bold by default.
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {res_x}
PlayResY: {res_y}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Base,{fontname},{style['font_size']},{primary},{outline_col},&H96000000,1,{style['outline']},{style['shadow']},{align},90,90,{cfg['video']['safe_zone_padding']},1
Style: Hook,{fontname},{int(style['font_size'] * 0.82)},{highlight},{outline_col},&H96000000,1,{style['outline'] + 1},{style['shadow']},8,80,80,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    # Animated hook title flashed top-of-frame for the first ~2.6s (pattern-interrupt).
    title_events = ""
    hook_dur = float(cfg["captions"].get("hook_title_seconds", 2.6))
    hook_title = _clean(hook_title)
    if hook_title:
        disp = hook_title.upper() if uppercase else hook_title
        disp = disp.replace("\n", " ").strip()
        title_events = (
            f"Dialogue: 0,{_ts(0.1)},{_ts(hook_dur)},Hook,,0,0,0,,"
            f"{{\\fad(150,250)\\fscx84\\fscy84\\t(0,220,\\fscx100\\fscy100)}}{disp}\n"
        )

    def animate_active(disp: str) -> str:
        # Scale "pop": 88% → 107% → 100% in the first ~170ms, bold + highlight color.
        return (
            f"{{\\b1\\1c{highlight}\\fscx88\\fscy88"
            f"\\t(0,90,\\fscx107\\fscy107)\\t(90,170,\\fscx100\\fscy100)}}"
            f"{disp}{{\\r}}"
        )

    lines = []
    # Group words into small cues; within a cue, the spoken word pops + highlights.
    for i in range(0, len(words), max_words):
        group = words[i : i + max_words]
        g_start, g_end = group[0][1], group[-1][2]
        for j, (tok, w_start, w_end) in enumerate(group):
            parts = []
            for k, (t2, _, _) in enumerate(group):
                disp = t2.upper() if uppercase else t2
                parts.append(animate_active(disp) if k == j else disp)
            text = " ".join(parts)
            # Gapless within the cue: hold each word until the next word begins.
            start = w_start if j > 0 else g_start
            end = group[j + 1][1] if j < len(group) - 1 else g_end
            lines.append(f"Dialogue: 0,{_ts(start)},{_ts(end)},Base,,0,0,0,,{text}")

    ass_path = out_dir / "captions.ass"
    ass_path.write_text(header + title_events + "\n".join(lines) + "\n", encoding="utf-8")
    log(f"captions: captions.ass ({len(words)} words, animated)", "ok")
    return ass_path
