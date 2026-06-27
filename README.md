# Video Autopilot 🎬🤖

A complete, self-hosted system that **generates and posts 1–3 faceless AI videos every day**
to **YouTube Shorts, Instagram Reels, Facebook Reels, and TikTok** — fully on autopilot.

It runs a daily pipeline: **trend/idea research → script → AI voiceover → visuals/B-roll →
word-by-word captions → 9:16 video assembly → thumbnail → SEO metadata → multi-platform
publish → analytics feedback loop.**

```
 ┌───────────┐   ┌──────────┐   ┌───────────┐   ┌──────────┐   ┌──────────┐
 │ IDEATION  │──▶│  SCRIPT  │──▶│ VOICEOVER │──▶│ VISUALS  │──▶│ CAPTIONS │
 │ trends/   │   │  hook+   │   │  TTS      │   │ AI img / │   │ word-by- │
 │ niche LLM │   │  beats   │   │  (11Labs/ │   │ stock    │   │ word ASS │
 └───────────┘   └──────────┘   │  edge)    │   │ B-roll   │   └────┬─────┘
                                └──────────┘   └──────────┘        │
        ┌──────────────────────────────────────────────────────────┘
        ▼
 ┌───────────┐   ┌──────────┐   ┌───────────────────────────┐   ┌───────────┐
 │ ASSEMBLE  │──▶│ METADATA │──▶│  PUBLISH                  │──▶│ ANALYTICS │
 │ ffmpeg    │   │ title/   │   │  YouTube · TikTok ·       │   │ pull KPIs │
 │ 9:16 1080 │   │ desc/tags│   │  IG/FB Reels (Ayrshare)   │   │ feedback  │
 └───────────┘   └──────────┘   └───────────────────────────┘   └───────────┘
```

---

## Table of contents

1. [What you get](#1-what-you-get)
2. [Requirements](#2-requirements)
3. [Install (10 minutes)](#3-install-10-minutes)
4. [Get your API keys](#4-get-your-api-keys)
5. [Configure your channels](#5-configure-your-channels)
6. [First run (dry-run)](#6-first-run-dry-run)
7. [The web dashboard](#7-the-web-dashboard)
8. [Going live (real publishing)](#8-going-live-real-publishing)
9. [Automate it (daily autopilot)](#9-automate-it-daily-autopilot)
10. [Local vs. cloud](#10-local-vs-cloud)
11. [Provider strategy & costs](#11-provider-strategy--costs)
12. [Project layout](#12-project-layout)
13. [Command reference](#13-command-reference)
14. [Troubleshooting](#14-troubleshooting)
15. [The strategy docs](#15-the-strategy-docs)

---

## 1. What you get

- **9-stage pipeline**, one Python module per stage — fully swappable providers.
- **A web dashboard** to generate, monitor, browse, and configure everything from the browser.
- **3 pre-built channels** (motivation, finance, psychology) you can run immediately.
- **A free path**: works end-to-end with $0/month providers (edge-tts + Pexels + local Whisper + dry-run).
- **An autopilot path**: one daily cron job builds and posts every channel's quota.
- **Anti-repeat memory** (`output/history.json`) so topics never duplicate across runs.
- **A complete strategy playbook** (niches, hooks, retention, monetization, compliance).

---

## 2. Requirements

| Need | Why | Notes |
|------|-----|-------|
| **macOS or Linux** | Host OS | This guide is macOS-first; Linux works with apt instead of brew. |
| **Python 3.9+** | Runs the pipeline | 3.10+ recommended; 3.9 works fine. |
| **ffmpeg** | Video/audio assembly | Installed automatically by the setup script. |
| **Homebrew** (macOS) | Installs ffmpeg | Get it at [brew.sh](https://brew.sh) if you don't have it. |
| **An LLM API key** | Scripts + ideas | **Anthropic Claude** (default) or OpenAI. Required. |
| **A Pexels API key** | Free stock B-roll | Free, unlimited. Required for the default visuals provider. |
| ~2 GB disk | Whisper model + renders | The caption model downloads once on first run. |

Everything else (premium voices, AI images, auto-publishing) is **optional** and opt-in.

---

## 3. Install (10 minutes)

```bash
cd /Users/aredwan/Documents/Projects/Video_Autopilot

# One-shot installer: installs ffmpeg, creates a .venv, installs deps,
# and downloads the default caption font.
bash scripts/install_mac.sh
```

This script:
1. Checks for Homebrew and installs **ffmpeg**.
2. Creates a Python virtual environment at `.venv`.
3. Installs all Python dependencies from `requirements.txt`.
4. Downloads the Montserrat ExtraBold caption font into `assets/fonts/`.

After it finishes, activate the environment for any manual commands:

```bash
source .venv/bin/activate
```

> **Optional but recommended:** drop 1–2 royalty-free music tracks (`.mp3`) into
> `assets/music/`. The assembler ducks them under the voiceover. Without music the
> videos still build — they're just silent under the narration.

---

## 4. Get your API keys

Copy the template and fill in **only** the providers you'll use:

```bash
cp .env.example .env
```

Then edit `.env`. **Minimum to start (both free):**

```ini
ANTHROPIC_API_KEY=sk-ant-...
PEXELS_API_KEY=...
```

### Where each key comes from

| Key | Get it at | Cost | Needed for |
|-----|-----------|------|------------|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) → API Keys | Pay-as-you-go (~$0.01–0.03/video). **Requires credits.** | Ideas + scripts (default LLM) |
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com) | Pay-as-you-go | Alternative LLM (`llm.provider: openai`) |
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | **Free tier** | Free LLM (`llm.provider: groq`) |
| `OPENROUTER_API_KEY` | [openrouter.ai/keys](https://openrouter.ai/keys) | **Free models available** | Free LLM (`llm.provider: openrouter`) |
| `GEMINI_API_KEY` | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | **Free tier** | Free LLM (`llm.provider: gemini`) |
| *(none — Ollama)* | [ollama.com](https://ollama.com) | **Free, local, no key** | Free offline LLM (`llm.provider: ollama`) |
| `PEXELS_API_KEY` | [pexels.com/api](https://www.pexels.com/api/) | **Free, unlimited** | Stock B-roll (default visuals) |
| `ELEVENLABS_API_KEY` | [elevenlabs.io](https://elevenlabs.io) | Free tier (10k chars/mo), then paid | Premium voiceover (optional) |
| `FAL_KEY` | [fal.ai](https://fal.ai) | Pay-per-image | AI-generated visuals (optional) |
| `REPLICATE_API_TOKEN` | [replicate.com](https://replicate.com) | Pay-per-image | AI-generated visuals (optional) |
| `AYRSHARE_API_KEY` | [ayrshare.com](https://www.ayrshare.com) | Paid (~$29/mo) | Auto-publish to all 4 platforms |
| `UPLOAD_POST_API_KEY` | [upload-post.com](https://upload-post.com) | Paid | Alternative publish aggregator |

> ⚠️ **Important formatting rule:** put each key's value on its own clean line with
> **no inline comments**. This is wrong and will be misread as a "configured" key:
> ```ini
> FAL_KEY=        # some comment   ← the comment becomes the value!
> ```
> Leave unused keys completely empty:
> ```ini
> FAL_KEY=
> ```

> 💡 The default `llm.model` is `claude-sonnet-4-6` (fast + cheap). For the highest
> script quality switch to `claude-opus-4-8` in `config/settings.yaml`.

### Choosing your LLM (including 100% free options)

The LLM writes your ideas and scripts. Set it in `config/settings.yaml` under `llm:` — no
code changes needed. You have six providers, including several **free** ones:

| `provider:` | Cost | Key needed | Suggested `model:` | Notes |
|-------------|------|------------|--------------------|-------|
| `anthropic` | Paid | `ANTHROPIC_API_KEY` | `claude-sonnet-4-6` / `claude-opus-4-8` | Best script quality (default) |
| `openai` | Paid | `OPENAI_API_KEY` | `gpt-4o-mini` / `gpt-4o` | Solid alternative |
| `ollama` | **Free** | none | `llama3.1` / `qwen2.5` | 100% local & offline — best free option |
| `groq` | **Free** | `GROQ_API_KEY` | `llama-3.3-70b-versatile` | Very fast, generous free tier |
| `openrouter` | **Free** | `OPENROUTER_API_KEY` | `meta-llama/llama-3.1-8b-instruct:free` | Many `:free` models |
| `gemini` | **Free** | `GEMINI_API_KEY` | `gemini-1.5-flash` | Google's free tier |

**Example — switch to free Groq:**
```yaml
llm:
  provider: groq
  model: llama-3.3-70b-versatile
  temperature: 0.9
```
…then put `GROQ_API_KEY=...` in `.env`. Done.

**Example — 100% free & offline with Ollama** (no API key, no internet, no cost):
```bash
# 1. Install Ollama → https://ollama.com  (or: brew install ollama)
ollama serve &           # start the local server
ollama pull llama3.1     # download a model once (~4.7 GB)
```
```yaml
# 2. config/settings.yaml
llm:
  provider: ollama
  model: llama3.1
  temperature: 0.9
```
No key required — Ollama runs entirely on your machine.

> Quality ranking for scripts: Claude/GPT (paid) ≥ Groq Llama-3.3-70B ≈ Gemini Flash >
> local Llama-3.1-8B. The free tiers are very usable; start free, upgrade only if scripts
> feel flat.

---

## 5. Configure your channels

Open `config/channels.yaml`. Three channels ship ready to run:

| Key | Name | Niche | Cadence |
|-----|------|-------|---------|
| `motivation` | Daily Discipline | motivation | 2/day |
| `money` | Money Mechanics | finance | 1/day |
| `facts` | Mind Blown Facts | psychology | 1/day |

Each block controls the niche, audience, angle, tone, voice, visual style, target platforms,
and `posts_per_day`. To add a channel, copy the commented template at the bottom of the file,
rename the key, and fill in the fields.

Global pipeline behavior (video size, caption style, loudness, providers, etc.) lives in
`config/settings.yaml`. Both files are editable from the dashboard's **Settings** tab, which
validates the YAML before saving.

---

## 6. First run (dry-run)

A **dry-run** builds a complete video locally **without posting anywhere** — your safe first test:

```bash
source .venv/bin/activate
python -m src.orchestrator --channel motivation --count 1 --dry-run
```

Watch the 9 stages run. When it finishes, your video and all its metadata are in:

```
output/<today>/motivation/<slug>/
├── final.mp4        ← the finished 9:16 video
├── script.txt       ← the voiceover script
├── voice.mp3        ← the narration
├── captions.ass     ← word-by-word captions
└── metadata.json    ← titles, description, hashtags, idea, publish result
```

Open `final.mp4` and review it. **Stay in dry-run** until you're happy with the script
quality, voice, captions, and pacing. Tweak prompts in `config/prompts/` and settings in
`config/settings.yaml`, then re-run.

---

## 7. The web dashboard

Prefer clicking to typing? Launch the control panel:

```bash
bash scripts/serve.sh            # → http://127.0.0.1:8000
```

| Tab | What it does |
|-----|--------------|
| **Dashboard** | Production stats, live activity feed, a "Get Started" setup checklist |
| **Generate** | Pick a channel, set count/dry-run, hit start, watch logs + pipeline stages stream live |
| **Library** | Play every generated video, search/filter by channel, view metadata, delete runs |
| **Channels** | Every account's niche, cadence, platforms, and how many videos it's produced |
| **Guide** | The complete playbook (niches, hooks, retention, monetization, compliance, FAQ) in-app |
| **Settings** | Edit `settings.yaml` / `channels.yaml` in-browser (YAML-validated), see detected API keys |

The sidebar shows green dots for which API keys are detected. The dashboard drives the **exact
same pipeline** as the CLI — it shells out to `src.orchestrator` as background jobs and streams
the logs back to your browser.

---

## 8. Going live (real publishing)

Once your dry-run videos look great:

1. **Sign up for a publish aggregator** — [Ayrshare](https://www.ayrshare.com) is the simplest:
   one API connects YouTube, TikTok, Instagram, and Facebook.
2. **Connect your social accounts** inside that provider's dashboard.
3. **Add the key** to `.env`:
   ```ini
   AYRSHARE_API_KEY=...
   ```
4. **Switch the provider** in `config/settings.yaml`:
   ```yaml
   publish:
     provider: ayrshare      # was: dry_run
   ```
5. **Run for real** (drop the `--dry-run` flag):
   ```bash
   python -m src.orchestrator --channel motivation --count 1
   ```

> Set `publish.queue: true` in `settings.yaml` to build + queue for manual review instead of
> posting live — a good intermediate step before full automation.

---

## 9. Automate it (daily autopilot)

`scripts/run_daily.sh` runs **every** channel for its `posts_per_day` quota — this is your
autopilot entrypoint:

```bash
bash scripts/run_daily.sh
```

### Option A — cron (Linux / always-on machine)

```bash
crontab -e
```

Add a line to run every day at 9:00 AM (logs to a file):

```cron
0 9 * * * /Users/aredwan/Documents/Projects/Video_Autopilot/scripts/run_daily.sh >> /Users/aredwan/Documents/Projects/Video_Autopilot/output/cron.log 2>&1
```

### Option B — macOS `launchd` (survives sleep better than cron)

cron only fires while the Mac is awake. For a laptop, a LaunchAgent with `StartCalendarInterval`
is more reliable, and you can pair it with `caffeinate`/"wake for network access" so the machine
wakes to run. Ask and the project can generate the `.plist` for you.

> ⚠️ Whichever you pick, the machine must be **on and awake** at run time. If you can't
> guarantee that, see the next section.

---

## 10. Local vs. cloud

The whole value of this system is **unattended daily posting**, so where it runs matters.

| | Local (your Mac) | Cloud VPS |
|---|---|---|
| **Cost** | Free | ~$6–12/month |
| **Best for** | Building, testing, reviewing output | True 24/7 autopilot |
| **Render speed** | Fast (your CPU) | Slower on cheap boxes (fine for 1–3/day) |
| **Reliability** | Only runs if the Mac is awake | Always on, survives reboots |
| **Setup effort** | None (already done) | ~10 min |

**Recommended path:**
1. **Now** → run **local + dry-run** until one channel looks great. Iteration is fastest here.
2. **Then** → local + real publish, to confirm posting works.
3. **For hands-off autopilot** → move to a cheap cloud VPS (Hetzner/DigitalOcean ~$6/mo) with
   the daily cron from §9. Your laptop stays free and posts happen even while you sleep.

**Zero-server option:** run it free on **GitHub Actions** — a scheduled workflow builds and
posts your videos daily with no VPS at all. The workflow ships in
[`.github/workflows/daily.yml`](.github/workflows/daily.yml); setup is in
[docs/DEPLOY.md → Path C](docs/DEPLOY.md#path-c--github-actions-free-no-server-at-all).

➡️ **Full step-by-step cloud setup (VPS + cron · Docker · GitHub Actions): [docs/DEPLOY.md](docs/DEPLOY.md).**

---

## 11. Provider strategy & costs

Every external service is a swappable adapter with a **free/cheap default** and a **premium
option**. Switch providers in `config/settings.yaml` — **no code changes**.

| Stage | Free / cheap default | Premium upgrade |
|-------|---------------------|-----------------|
| LLM (ideas+script) | **Ollama** (local) · **Groq / OpenRouter / Gemini** (free tiers) | **Claude** (`claude-opus-4-8`/`claude-sonnet-4-6`) or GPT |
| Voiceover | `edge-tts` (free, no key) | **ElevenLabs** (best retention) |
| Visuals | **Pexels** stock (free) | AI images (fal / Replicate) |
| Captions | `faster-whisper` (local, free) | — |
| Assembly | **ffmpeg** (free) | — |
| Publishing | `dry_run` (free, local only) | **Ayrshare / upload-post** (1 API → all 4 platforms) |

**100% free setup:** Ollama (or Groq) + edge-tts + Pexels + local Whisper + dry-run/manual
upload — **$0/month**. Add a paid publish aggregator only when you want true auto-posting.

**Best-quality cheap setup:** Claude Sonnet + edge-tts + Pexels + local Whisper + Ayrshare.
LLM cost is roughly **$0.01–0.03 per video**; the only fixed cost is the publish aggregator.

---

## 12. Project layout

```
config/        settings.yaml · channels.yaml · prompts/    ← what to make
src/           the 9-stage pipeline (one module per stage)
  ├── orchestrator.py   runs all stages; CLI entrypoint
  ├── ideation.py       stage 1 — pick a viral idea
  ├── scriptwriter.py   stage 2 — hook + beats + closer
  ├── voiceover.py      stage 3 — TTS narration
  ├── visuals.py        stage 4 — stock/AI B-roll
  ├── captions.py       stage 5 — word-level ASS captions
  ├── assemble.py       stage 6 — ffmpeg 9:16 render
  ├── metadata.py       stage 7 — titles/desc/hashtags
  ├── publish.py        stage 8 — multi-platform post
  ├── analytics.py      stage 9 — KPI feedback loop
  ├── config.py         loads settings + channels + .env
  └── utils.py          logging, slugs, JSON parsing, history
webapp/        FastAPI dashboard + no-build web UI (static/)
assets/        music · fonts · overlays (you supply licensed assets)
output/        generated videos + metadata json per run · history.json
scripts/       install_mac.sh · run_daily.sh · serve.sh
docs/          the human strategy guidelines
```

---

## 13. Command reference

All commands assume the venv is active (`source .venv/bin/activate`). The `Makefile` wraps
the common ones:

| Make | Equivalent | Does |
|------|-----------|------|
| `make install` | `bash scripts/install_mac.sh` | Install ffmpeg + venv + deps |
| `make serve` | `bash scripts/serve.sh` | Launch the dashboard |
| `make dry CH=money` | `python -m src.orchestrator --channel money --count 1 --dry-run` | Build 1 video locally, no posting |
| `make run CH=money` | `python -m src.orchestrator --channel money --count 1` | Build + publish 1 video |
| `make all` | `python -m src.orchestrator --all` | Run every channel (the daily job) |
| `make report` | `python -m src.orchestrator --report` | Print the analytics/feedback report |
| `make clean` | — | Remove generated output (keeps `history.json`) |

**Raw orchestrator flags:**

```bash
python -m src.orchestrator --channel <key>   # which channel block to run
                           --count <n>        # how many videos this run (default 1)
                           --all              # every channel, posts_per_day each
                           --dry-run          # build locally, do not post
                           --report           # print analytics report and exit
```

---

## 14. Troubleshooting

| Symptom | Cause & fix |
|---------|-------------|
| `Your credit balance is too low` | Your Anthropic account has no credits. Add some at [console.anthropic.com](https://console.anthropic.com) → Plans & Billing (even $5 lasts for hundreds of videos), or switch to a **free** LLM (Ollama/Groq/Gemini) in `settings.yaml` — see [Choosing your LLM](#choosing-your-llm-including-100-free-options). |
| `<KEY> missing in .env` | The provider you selected in `settings.yaml` needs that key. Add it to `.env`, or switch to `ollama` (no key needed). |
| Dashboard shows keys you didn't add | Old bug from inline comments in `.env`. Make sure each unused key line is empty with no trailing `# comment`. |
| `NotOpenSSLWarning: ... LibreSSL` | Harmless warning from system Python's old SSL. Ignore it, or use the `.venv` Python. |
| `ffmpeg: command not found` | Re-run `bash scripts/install_mac.sh` — it auto-downloads a static ffmpeg into `.venv/bin` even **without Homebrew**. (With brew: `brew install ffmpeg`.) Note: ffmpeg lives in the venv, so activate it (`source .venv/bin/activate`) before CLI runs. |
| Captions stage is slow the first time | `faster-whisper` downloads its model once (~150 MB for `base`). Subsequent runs are fast. |
| Video has no background music | Add `.mp3` files to `assets/music/`. Videos build silent-under-narration without it. |
| Whisper too slow / inaccurate | Change `captions.model` in `settings.yaml`: `tiny` (fastest) → `base` → `small` (most accurate). |
| Publish does nothing | Check `publish.provider` isn't `dry_run`, the aggregator key is in `.env`, and your social accounts are connected in the aggregator's dashboard. |

---

## 15. The strategy docs

The code makes videos; these docs make them *win*:

| Doc | What it covers |
|-----|----------------|
| **[ROADMAP.md](ROADMAP.md)** | Progress tracker — what's shipped, in progress, and planned |
| **[docs/SETUP.md](docs/SETUP.md)** | Deeper install, account setup, API keys, first run |
| **[docs/DEPLOY.md](docs/DEPLOY.md)** | Cloud deployment — VPS + cron or Docker, for unattended daily posting |
| **[docs/PLAYBOOK.md](docs/PLAYBOOK.md)** | The strategy: niches, viral hooks, retention, cadence, monetization, scaling |
| **[docs/COMPLIANCE.md](docs/COMPLIANCE.md)** | Platform rules, AI-disclosure, monetization eligibility, how to NOT get banned |

### The honest economics

This is a **portfolio + volume** game, not a lottery ticket. One channel rarely pays;
**5–10 channels × 1–3 posts/day × 90 days** is the real unit of success. See the revenue
math, payout thresholds, and reinvestment plan in
**[docs/PLAYBOOK.md](docs/PLAYBOOK.md#-the-money)**.

> ⚖️ **Use responsibly.** Respect each platform's automation, spam, and AI-content rules
> (see [docs/COMPLIANCE.md](docs/COMPLIANCE.md)). Don't post misinformation, don't impersonate,
> label AI where required, and only use licensed/royalty-free assets. Accounts that mass-spam
> low-effort reposts get deranked or banned — this system is built to produce *original,
> high-quality* content at scale.
