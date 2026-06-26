# The Playbook — Strategy, Virality & Revenue

This is the *thinking* behind the machine. The code makes videos; this doc makes them **work**.

---

## 1. Pick a niche that pays (the most important decision)

Faceless success = **a niche with high RPM + infinite content + emotional pull**. Score each
candidate 1–5 on the four axes below; only build channels that total ≥14.

| Axis | Question |
|------|----------|
| **Monetizable** | Do advertisers pay a high RPM here? (finance, business, tech, health > comedy memes) |
| **Repeatable** | Can you make 300+ videos without running dry? |
| **Emotional** | Does it trigger awe, fear, curiosity, motivation, or "I need to save this"? |
| **Faceless-fit** | Can it be told with voiceover + stock/AI visuals (no presenter needed)? |

### Proven faceless niches (and their angle)

| Niche | Why it works | RPM tier |
|-------|-------------|----------|
| 💪 **Motivation / discipline** | Endlessly remixable, huge saves/shares | Low-Mid |
| 💰 **Personal finance / money tips** | High advertiser RPM, save-worthy | **High** |
| 🧠 **Psychology / "did you know" facts** | Curiosity loop, broad appeal | Mid |
| 🏛️ **History / "what they didn't tell you"** | Story-driven, strong retention | Mid |
| 🤖 **AI tools / tech news** | Trending, shareable, high RPM | **High** |
| 🩺 **Health / longevity / sleep** | Save-worthy, high RPM, careful claims | High |
| 😱 **Scary stories / unsolved mysteries** | Binge retention, strong watch time | Low-Mid |
| 🧘 **Stoic philosophy** | Premium aesthetic, loyal audience | Mid |
| 📈 **Business / side-hustle breakdowns** | High RPM, entrepreneurial audience | **High** |

> **Rule:** one niche **per channel/account**. The algorithm rewards a consistent topic
> signal. Run *several* single-niche channels rather than one mixed channel.

Configure niches in [`config/channels.yaml`](../config/channels.yaml).

---

## 2. Anatomy of a video that goes viral (Short/Reel/TikTok, 20–45s)

```
0.0–1.5s   HOOK        Stop the scroll. Visual motion + a verbal pattern-interrupt.
1.5–4s     PROMISE     Tell them what they'll get / why to stay ("...and #3 will shock you").
4–30s      VALUE       3–5 punchy beats. One idea per beat. Visual changes every 2–3s.
30–40s     PAYOFF      Deliver the promise. The "save this" moment.
last 2s    LOOP/CTA    Loop the first frame OR a soft CTA ("Follow for part 2").
```

### Hook formulas that stop the scroll (first 3 seconds decide everything)
- **Negative/contrarian:** "Stop doing ___ if you want ___."
- **Curiosity gap:** "Nobody talks about what happens when ___."
- **Number + payoff:** "5 ___ that ___ (the last one is free)."
- **Direct address:** "If you're under 30, watch this."
- **Bold claim:** "This is the most underrated ___ of all time."
- **Question:** "Why do the richest people never ___?"

### Retention rules (these drive the algorithm more than anything)
1. **Visual cut every 2–3 seconds.** Static = scroll-away.
2. **Word-by-word captions, always.** 85% watch muted. This system burns them in.
3. **No dead air.** Voiceover starts at 0.0s. No intros, no logos.
4. **Pace the audio fast** (1.05–1.15× speed feels energetic).
5. **Loop-ability:** end where you began so replays inflate watch time.
6. **One idea per video.** Confusion kills retention.

> The pipeline encodes these in `config/settings.yaml` (cut cadence, caption style,
> speed, target duration) and in `config/prompts/script.md` (hook + beat structure).

---

## 3. Posting cadence & scheduling

| Channels | Posts/day/channel | Best slots (local audience time) |
|----------|-------------------|----------------------------------|
| Start (week 1–4) | 1 | 1 strong post beats 3 weak ones |
| Growth (month 2+) | 2–3 | morning 7–9am · midday 12–1pm · evening 7–10pm |

- **Consistency > volume.** Same times daily trains the algorithm and the audience.
- **Stagger platforms by a few minutes** (don't fire identical posts simultaneously).
- **Don't post the *byte-identical* file to all 4 platforms** — the system re-encodes per
  platform (aspect/safe-zones/loudness) so each upload is platform-native. See `publish.py`.
- TikTok/Reels reward **native trends & sounds**; YouTube Shorts rewards **searchable titles**.

Automate via cron — see [SETUP.md](SETUP.md#5-automate-with-cron).

---

## 4. Per-platform optimization

| | YouTube Shorts | TikTok | Instagram Reels | Facebook Reels |
|--|--|--|--|--|
| **Length sweet spot** | 25–40s | 21–34s | 20–35s | 25–45s |
| **What ranks it** | Title keywords + watch % | Sound + completion + shares | Shares/saves + watch % | Shares + watch time |
| **Caption** | SEO title + 3–5 hashtags | 3–5 trending hashtags, hook in caption | hook + 3–5 niche hashtags | short hook, fewer tags |
| **Edge** | searchable, evergreen | fastest viral velocity | best for saves/aesthetic | older audience, high RPM |
| **Avoid** | other-platform watermarks | other-platform watermarks (TikTok suppresses them) | <-- same | <-- same |

> ⚠️ **Watermarks matter.** Never upload a TikTok-watermarked file to Reels/Shorts (and vice
> versa). This system renders **one clean master with no watermark** and uploads that everywhere.

---

## 5. SEO & metadata (where free reach is won)

- **Title:** front-load the keyword + curiosity. `metadata.py` generates 3 variants; pick best.
- **Description:** 1–2 line hook + keyword + soft CTA + hashtags.
- **Hashtags:** 3–5 **niche** tags (not `#fyp #viral` only — mix 1 broad + 3 niche + 1 branded).
- **First comment:** pin a question to spark replies (comments = ranking signal).
- **Thumbnail (Shorts):** high-contrast face/object + ≤3 words of bold text.

---

## 6. The money 💰

### Revenue streams (stack them — never rely on one)
1. **Platform ad share** — YouTube Shorts Fund/ads, TikTok Creativity Program, IG/FB bonuses.
2. **Affiliate links** — bio + pinned comment (highest early ROI, no follower minimum).
3. **Digital product** — your own ebook/template/Notion/course once you have an audience.
4. **Brand deals / UGC** — once a channel proves a niche audience.
5. **Channel as an asset** — faceless channels sell for 20–40× monthly profit.

### Monetization thresholds (verify current numbers — they change)
| Platform | Rough gate to ad revenue |
|----------|--------------------------|
| YouTube (Shorts) | 1,000 subs + 10M Shorts views in 90 days *(or 4,000 watch-hrs)* |
| TikTok Creativity | 10,000 followers + 100,000 views / 30 days, 1-min+ videos |
| Instagram/Facebook | invite-based bonuses + affiliate/brand the reliable path |

### Realistic expectations (set these now)
- **It's a portfolio game.** Plan for **5–10 channels**, expect most to be mediocre and a few
  to carry the revenue. Don't judge before **90 days / ~90 posts** per channel.
- **Affiliate + your own product** usually beats ad-share for the first 6 months.
- **Reinvest** early revenue into ElevenLabs voices + AI visuals + the publishing API — these
  lift retention/CTR, which compounds. Math lives in `analytics.py`'s report.

### The growth flywheel the system runs
```
post daily → analytics.py pulls top performers → feeds winning hooks/topics back into
ideation.py → next batch biases toward what worked → retention rises → more reach → repeat
```

---

## 7. Scaling to a content factory

1. **Templatize per niche** (intro style, font, music, color) so output is recognizable.
2. **Batch generate** a week of videos in one run; schedule the drip (don't dump).
3. **Add channels, not complexity** — clone a `channels.yaml` block, change the niche+voice.
4. **Repurpose** long ideas into multi-part series ("Part 1/5") to farm follows & returns.
5. **Localize** winners into other languages (new TTS voice + translated script = new market).
6. **Kill losers fast.** A channel with no traction after 60–90 posts → repurpose the slot.

---

## 8. Daily operator checklist (5 min/day)

- [ ] `run_daily.sh` ran for every channel (check `output/` + publish logs)
- [ ] Skim each posted video for caption sync / visual glitches
- [ ] Reply to top 3 comments per channel (engagement signal + ideas)
- [ ] Once/week: read `analytics.py` report, prune dead channels, double down on winners
- [ ] Once/week: top up trend list & refresh hooks in `config/prompts/`
