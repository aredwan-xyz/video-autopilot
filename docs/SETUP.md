# Setup

## 0. What you need

- **macOS/Linux**, Python 3.9+, ~5 GB free (models + media)
- **ffmpeg** (video assembly) — installed by `install_mac.sh`
- API keys (pick the ones matching your provider choices in `config/settings.yaml`):

| Purpose | Provider | Free tier? | Get key |
|---------|----------|-----------|---------|
| Scripts/ideas | **Anthropic (Claude)** | trial credit | console.anthropic.com |
| or | OpenAI | trial credit | platform.openai.com |
| Voiceover (premium) | **ElevenLabs** | 10k chars/mo free | elevenlabs.io |
| Voiceover (free) | `edge-tts` | 100% free | no key needed |
| Stock visuals (free) | **Pexels** | free | pexels.com/api |
| AI visuals (premium) | fal.ai / Replicate | pay-as-go | fal.ai · replicate.com |
| Publishing (all 4) | **Ayrshare** | free tier | ayrshare.com |
| or | upload-post.com | free tier | upload-post.com |

> You can run the whole thing on **free tiers** (edge-tts + Pexels + local Whisper + manual
> upload) and upgrade stages one at a time as revenue comes in.

## 1. Install

```bash
bash scripts/install_mac.sh
```

This installs ffmpeg (via Homebrew), creates a `.venv`, and installs `requirements.txt`.
On Linux, install `ffmpeg` from your package manager, then:

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

## 2. Configure secrets

```bash
cp .env.example .env
```

Open `.env` and fill in **only the keys for the providers you chose**. Leave the rest blank.

## 3. Choose providers & global settings

Edit [`config/settings.yaml`](../config/settings.yaml):

```yaml
llm:        { provider: anthropic, model: claude-sonnet-4-6 }
tts:        { provider: edge }          # edge (free) | elevenlabs
visuals:    { provider: pexels }        # pexels | fal | replicate
publish:    { provider: dry_run }       # dry_run | ayrshare | upload_post
```

Start with `tts: edge`, `visuals: pexels`, `publish: dry_run` to validate the pipeline for free.

## 4. Pick your niche(s)

Edit [`config/channels.yaml`](../config/channels.yaml). Each block = one channel/account.
Set the niche, voice, visual style, target platforms, and per-channel API tokens.

## 5. First run

```bash
source .venv/bin/activate

# Build ONE video locally, no posting:
python -m src.orchestrator --channel motivation --count 1 --dry-run

# Output lands in output/<date>/<channel>/<slug>/
#   final.mp4 · script.txt · voice.mp3 · captions.ass · metadata.json
```

Watch `final.mp4`. Tune `settings.yaml` (caption font/size, cut cadence, music volume) until
it looks right. **Then** flip `publish.provider` to a real provider and drop `--dry-run`.

## 6. Automate with cron

```bash
crontab -e
```

```cron
# 1 video/channel at 8am, a 2nd batch at 6pm (2/day). Adjust to taste.
0 8  * * *  /Users/aredwan/Documents/Projects/Video_Autopilot/scripts/run_daily.sh >> ~/va.log 2>&1
0 18 * * *  /Users/aredwan/Documents/Projects/Video_Autopilot/scripts/run_daily.sh >> ~/va.log 2>&1
```

`run_daily.sh` loops over every channel in `channels.yaml` and runs the pipeline. For true
"set-and-forget" while your Mac sleeps, run it on a cheap always-on VPS or a Raspberry Pi.

> Prefer scheduled *generation* + *queued* posting over instant posting, so you can eyeball
> the batch before it goes live during your first few weeks. Set `publish.queue: true`.

## 7. Verify a healthy run

```
✓ ideation     → 1 idea picked from N trends
✓ script       → hook + 4 beats, ~90 words
✓ voiceover    → voice.mp3 (28s)
✓ visuals      → 12 clips downloaded
✓ captions     → captions.ass (word-level)
✓ assemble     → final.mp4 (1080x1920, 30fps)
✓ metadata     → 3 title variants + tags
✓ publish      → [dry-run] would post to youtube, tiktok, instagram, facebook
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ffmpeg: command not found` | `brew install ffmpeg` |
| Whisper slow/crashes | set `captions.model: tiny` or `base` in settings.yaml |
| Pexels 429 | you hit rate limit — add a key or slow `--count` |
| Voice sounds robotic | switch `tts.provider: elevenlabs` |
| Captions out of sync | ensure voiceover sample rate is 44.1k; re-run captions stage |
| Publish auth fails | re-check token in `.env`; confirm platform connected in Ayrshare dashboard |
