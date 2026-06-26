# Cloud Deployment Guide

How to run Video Autopilot on a cloud server so it builds and posts videos **every day,
unattended**, without your laptop being on.

---

## What kind of cloud? (read this first)

This app is **not** a fit for serverless / PaaS (Vercel, Netlify, Lambda, Cloud Run). Here's why:

- Each video render runs **ffmpeg + Whisper** for minutes — past serverless time limits.
- It needs a **persistent cron schedule** and **local disk** for the Whisper model + output.
- It's a long-lived worker, not a request/response web app.

➡️ **Use a small Linux VPS** (a plain virtual server). That's the right tool, and it's cheap.

| Provider | Plan | ~Cost/mo | Notes |
|----------|------|----------|-------|
| **Hetzner Cloud** | CX22 (2 vCPU, 4 GB) | ~€4 | Best price/perf; recommended |
| **DigitalOcean** | Basic 2 GB | ~$12 | Simple UI, lots of guides |
| **Vultr / Linode** | 2 GB | ~$10–12 | Equivalent |

**Specs to target:** 2 vCPU, 4 GB RAM, 40 GB+ disk, **Ubuntu 24.04**. 1 vCPU/2 GB works for
1–2 videos/day but renders slower. Pick a region near you for faster uploads.

---

## Path A — VPS + cron (recommended, ~15 min)

The simplest reliable setup: install once, schedule a daily cron job.

### 1. Create the server
Spin up an Ubuntu 24.04 VPS from any provider above. Add your SSH key during creation, then:

```bash
ssh root@YOUR_SERVER_IP
```

### 2. Get the code onto it
Either `git clone` your repo, or copy from your Mac with `rsync` (skips local junk):

```bash
# from your Mac:
rsync -av --exclude .venv --exclude output --exclude '*.pyc' \
  ~/Documents/Projects/Video_Autopilot/ root@YOUR_SERVER_IP:/root/Video_Autopilot/
```

### 3. Install everything (one command)

```bash
cd /root/Video_Autopilot
bash scripts/setup_ubuntu.sh
```

This installs ffmpeg + a Python venv + all dependencies and the caption font — the Linux
equivalent of the macOS installer.

### 4. Configure keys + providers

```bash
cp .env.example .env
nano .env                      # paste your GROQ_API_KEY, PEXELS_API_KEY, publish key, etc.
nano config/settings.yaml      # set llm.provider + publish.provider
```

### 5. Test it (dry-run, no posting)

```bash
source .venv/bin/activate
python -m src.orchestrator --channel motivation --count 1 --dry-run
```

You should get a `final.mp4` under `output/`. If this works, the box is ready.

### 6. Schedule the daily autopilot

Find your full repo path (`pwd`) then edit cron:

```bash
crontab -e
```

Add a line — runs every day at 09:00 server time, logs to a file:

```cron
0 9 * * * cd /root/Video_Autopilot && /root/Video_Autopilot/scripts/run_daily.sh >> /root/Video_Autopilot/output/cron.log 2>&1
```

> `run_daily.sh` runs **every channel** for its `posts_per_day` quota. Check it worked the next
> day with `tail -f /root/Video_Autopilot/output/cron.log`.

That's it — your server now produces and posts videos daily on its own.

---

## Path B — Docker (portable, reproducible)

If you prefer containers (same image runs anywhere):

```bash
# On the server, in the repo dir, after creating .env:
docker compose up -d web                 # dashboard at http://SERVER_IP:8000
docker compose run --rm daily            # one full pipeline run (all channels)
```

Schedule the daily job from the **host** crontab (not inside the container):

```cron
0 9 * * * cd /root/Video_Autopilot && docker compose run --rm daily >> output/cron.log 2>&1
```

The `Dockerfile` and `docker-compose.yml` are in the repo root. `output/` and `config/` are
mounted as volumes so your videos and settings persist outside the container.

---

## Path C — GitHub Actions (FREE, no server at all)

The daily job is a perfect fit for GitHub's free scheduled workflows — **no VPS, $0/month.**
The repo already ships the workflow at [`.github/workflows/daily.yml`](../.github/workflows/daily.yml).

**How it works:** GitHub runs an Ubuntu machine on a cron schedule, builds your videos, posts
them (via your publish provider), commits the updated topic-history back to the repo so
anti-repeat memory persists, and uploads the built `.mp4`s as downloadable artifacts.

### Setup (~5 min)

1. **Push this repo to GitHub** (private repo recommended):
   ```bash
   git init && git add . && git commit -m "initial"
   gh repo create video-autopilot --private --source=. --push
   ```
2. **Add your keys as Secrets:** repo → **Settings → Secrets and variables → Actions → New
   repository secret.** Add the ones you use, e.g. `GROQ_API_KEY`, `PEXELS_API_KEY`, and
   (for live posting) `AYRSHARE_API_KEY`. The workflow already maps all of them.
3. **Commit your providers:** `config/settings.yaml` is in the repo, so set `llm.provider`
   and `publish.provider` there. (It defaults to `dry_run`, so nothing posts until you change it.)
4. **Test it:** repo → **Actions → Daily Video Autopilot → Run workflow.** Leave "dry_run"
   checked, optionally set a single channel, and run. Download the result from the run's
   **Artifacts**.
5. **Go live:** set `publish.provider: ayrshare` in `settings.yaml`, push, and the daily 09:00
   UTC schedule will post automatically.

### Good to know

- **Cost:** free tier is 2,000 min/month for private repos (public repos are unlimited). A few
  videos/day stays well under it. ffmpeg is pre-installed on the runners; the Whisper model is
  cached between runs.
- **Timing:** the cron is **UTC** and scheduled runs can be delayed a few minutes under load —
  irrelevant for daily videos. Edit the `cron:` line to change the time.
- **Manual runs** always honor the "dry_run" checkbox; **scheduled runs** follow
  `settings.yaml` (so they post only once you set a real publish provider).
- **Limit:** there's no dashboard here — Actions is a headless runner. Use Path A/B if you want
  the live UI, or run the dashboard locally and let Actions handle production.

---

## Accessing the dashboard remotely (optional)

You usually don't need the dashboard on a server — cron does the work. But to monitor it:

### Easiest & safest — SSH tunnel (nothing exposed publicly)

Start the dashboard on the server bound to localhost:

```bash
# on the server:
bash scripts/serve.sh        # serves on 127.0.0.1:8000
```

Then from your Mac, tunnel to it:

```bash
ssh -L 8000:localhost:8000 root@YOUR_SERVER_IP
```

Open **http://localhost:8000** on your Mac — you're viewing the server's dashboard over the
encrypted SSH connection. Nothing is exposed to the internet.

### Persistent public access — reverse proxy + auth

Only if you want it reachable from a browser anywhere. **Never expose it raw** — it can edit
config and trigger jobs. Put nginx in front with HTTP basic-auth (or Caddy with `basicauth`),
bind uvicorn to `127.0.0.1`, and open only port 443 in the firewall. Ask and a config can be
generated for you.

---

## Keep it running & healthy

- **Run dashboard as a service** (so it survives reboots) — create a `systemd` unit that runs
  `scripts/serve.sh`, or use Docker's `restart: unless-stopped` (already set in compose).
- **Disk**: each video is ~3–6 MB plus its source clips. Add `make clean` to a weekly cron to
  prune old `output/` runs (it keeps `history.json` so anti-repeat still works).
- **Timezone**: cron uses the server's clock. Set it with `sudo timedatectl set-timezone Region/City`
  so "9am" means your 9am.
- **Firewall**: `ufw allow OpenSSH` then `ufw enable`. Don't open 8000 unless you've added auth.
- **Logs**: `tail -f output/cron.log` after the first scheduled run to confirm it fired.

---

## Cost summary

| Piece | Cost |
|-------|------|
| VPS (Hetzner CX22) | ~€4/mo |
| LLM (Groq free tier) | $0 |
| Voice (edge-tts) | $0 |
| Visuals (Pexels) | $0 |
| Captions (local Whisper) | $0 |
| Publishing (Ayrshare) | ~$29/mo (only when you go live) |

**Free-while-testing:** keep `publish.provider: dry_run` and you pay only the ~€4 VPS while you
dial things in. Add the publish aggregator when you're ready to actually post.
