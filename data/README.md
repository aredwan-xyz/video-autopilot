# Your content data

Drop your existing content here and the pipeline will **learn from it** every run — matching
your voice and following your strategy instead of starting cold.

## Where to put things

```
data/
├── scripts/      ← your past video scripts / captions / post text   (.txt or .md)
│   └── <channel_key>/   (optional: scripts just for one channel, e.g. data/scripts/motivation/)
└── notes/        ← your strategy: content pillars, brand voice, do/don't, audience  (.txt or .md)
    └── <channel_key>/   (optional: notes just for one channel)
```

- **`scripts/`** — examples of content you've made (or admire). The scriptwriter studies these
  to match your **voice, rhythm, and structure**.
- **`notes/`** — your **strategy and guidance**: who the audience is, your angle, words to use
  or avoid, recurring themes, what's worked. This steers ideation and scriptwriting.
- One file per piece is fine; `.txt` and `.md` are both read. Filenames don't matter.
- **Per-channel:** put files in `scripts/<channel_key>/` or `notes/<channel_key>/` to apply them
  to just that channel (keys come from `config/channels.yaml`, e.g. `motivation`, `money`, `facts`).
  Files directly in `scripts/` and `notes/` apply to **all** channels.

## Privacy (important — this repo is public)

Your dropped files are **git-ignored by default**, so your scripts and notes are NOT published.
They work for **local runs** immediately.

To let the **cloud autopilot (GitHub Actions)** use them too, you must commit them — which makes
them public. Either:
- keep them local-only (private, but cloud runs won't see them), **or**
- force-add them (`git add -f data/scripts data/notes`) to use them in the cloud, accepting
  they become visible in the public repo. Make a private repo first if that matters.

## Limits
Injected context is capped (~4k chars of scripts, ~3k of notes per run) to control cost — the
most recent/relevant files are used first.
