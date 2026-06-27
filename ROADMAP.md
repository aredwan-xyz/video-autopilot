# Roadmap & Progress Tracker

The single source of truth for what's shipped, in progress, and planned for Video Autopilot.
Tick a box when something ships, move rows between sections, and keep the dates current.

**Status legend:** ✅ shipped · 🚧 in progress · 📋 planned · 🧊 icebox (later/maybe)
**Impact / Effort / Cost:** 🔥 high · 🟡 medium · ⚪ low · 💲 needs paid service

_Last updated: 2026-06-26_

---

## ✅ Shipped

### Foundation
- [x] 9-stage pipeline (ideation → script → voice → visuals → captions → assemble → metadata → publish → analytics)
- [x] Multi-provider LLM: Anthropic, OpenAI, **Ollama, Groq, OpenRouter, Gemini** (free options)
- [x] Auto-retry on LLM rate limits (honors `Retry-After`)
- [x] Free stack working end-to-end (Groq + edge-tts + Pexels + Whisper + ffmpeg)
- [x] Web dashboard (generate, library, channels, guide, settings)
- [x] Anti-repeat topic memory (`output/history.json`)

### Deploy & infra
- [x] Local installer (macOS, with no-Homebrew static ffmpeg fallback)
- [x] Cloud deploy guide — VPS + cron, Docker, GitHub Actions ([docs/DEPLOY.md](docs/DEPLOY.md))
- [x] **GitHub Actions daily workflow** — free, no-server autopilot ([.github/workflows/daily.yml](.github/workflows/daily.yml))
- [x] Public repo + GitHub Pages showcase site
- [x] Secret-safe (`.env` excluded, scanned before publish)

### World-class quality upgrade (v1)
- [x] Ideation: viral frameworks + SEO/AEO/GEO searchable topic framing
- [x] Script: hook formulas, retention engineering, open loops, mid-video re-hook, length enforcement
- [x] Audio: broadcast mastering chain (compression, presence EQ, de-ess, −14 LUFS, limiter)
- [x] Captions: animated word-pop highlight, hook-title overlay, smart wrapping, gapless timing
- [x] Assembly: alternating Ken Burns, color grade + vignette, sidechain-ducked music, CRF-19
- [x] Metadata: keyword-front-loaded titles, answer-engine descriptions, keyword/entity tags
- [x] Visuals: smarter Pexels selection (HD portrait, no repeats) mapped per-beat

---

## 🚧 In progress

_(nothing active — pull the next item from Planned)_

---

## 📋 Planned — ranked by impact

### Phase 2 — biggest wins (free, code)
| # | Feature | Impact | Effort | Cost | Status |
|---|---------|--------|--------|------|--------|
| 1 | **Sound design** — SFX/whooshes on cuts, ding on reveals, hook bass-drop | 🔥 | 🟡 | free | 📋 |
| 2 | **Real trend data → ideation** (Google Trends, YT autocomplete, Reddit) | 🔥 | 🟡 | free | 📋 |
| 3 | **Beat-synced cuts** — align segment boundaries to the music beat | 🔥 | 🟡 | free | 📋 |
| 4 | **Transitions & zoom-punch** — whip-pans, emphasis zooms, hook punch | 🔥 | 🟡 | free | 📋 |

### Phase 3 — visual richness
| # | Feature | Impact | Effort | Cost | Status |
|---|---------|--------|--------|------|--------|
| 5 | Mixed media — blend stock + AI images + text cards (+ AI video) | 🟡 | 🟡 | free–💲 | 📋 |
| 6 | Motion-graphics overlays — arrows, highlights, emoji, keyword pops | 🟡 | 🟡 | free | 📋 |
| 7 | Brand kit — intro sting, logo bug, channel color, CTA end-card | 🟡 | 🟡 | free | 📋 |
| 8 | Auto-reframe / subject tracking crop for person B-roll | ⚪ | 🔥 | free | 🧊 |

### Phase 4 — audio
| # | Feature | Impact | Effort | Cost | Status |
|---|---------|--------|--------|------|--------|
| 9 | Premium voice (ElevenLabs) — realism ceiling | 🔥 | ⚪ | 💲 | 📋 |
| 10 | Mood-matched music selection (by channel energy/emotion) | 🟡 | ⚪ | free | 📋 |

### Phase 5 — data-driven (compounding)
| # | Feature | Impact | Effort | Cost | Status |
|---|---------|--------|--------|------|--------|
| 11 | Real analytics feedback loop — pull KPIs, double down on winners | 🔥 | 🔥 | free–💲 | 📋 |
| 12 | Hook A/B testing across platforms | 🟡 | 🟡 | free | 📋 |
| 13 | Per-platform optimization (safe-zones, hashtags, hook length, timing) | 🟡 | 🟡 | free | 📋 |

### Phase 6 — quality & longevity
| # | Feature | Impact | Effort | Cost | Status |
|---|---------|--------|--------|------|--------|
| 14 | Automated QC gate (audio clip, caption sync, black frames, duration) | 🟡 | 🟡 | free | 📋 |
| 15 | Template variety — rotate caption styles/layouts (anti-fatigue) | ⚪ | ⚪ | free | 📋 |

---

## 🧊 Icebox / ideas
- AI talking-avatar option (HeyGen-style) for a face-optional variant
- Multi-language dubbing (one script → many locales) for reach
- Thumbnail/cover A/B generation
- Comment auto-reply bot to boost engagement signals
- Web dashboard: live roadmap view that reads this file

---

## How to use this tracker
- **Starting a feature?** Move its row to **🚧 In progress** and set status 🚧.
- **Shipped?** Check the box, move it to **✅ Shipped** under the right group, bump the date.
- **New idea?** Add it to **📋 Planned** (with impact/effort/cost) or **🧊 Icebox**.
- Keep one item in progress at a time for focus; pull the highest-impact 📋 next.

> Tip: every shipped feature should leave a trace — a commit referencing the `#` here, and
> a one-line entry so this doubles as the changelog.
