# Compliance & Staying Un-banned

Automation at scale is allowed — **low-effort spam and rule-breaking is what gets punished.**
Read this once; it protects the asset you're building.

## Golden rules
1. **Original > reposted.** Don't rip and re-upload others' clips. This system generates
   original scripts + your own voiceover + licensed/AI visuals. That's the whole point.
2. **Label AI content where required.** YouTube, TikTok, Instagram/Meta all require disclosure
   of realistic AI-generated/altered media. The pipeline can stamp an "AI-assisted" note in the
   description and set the platform's synthetic-media flag — keep `compliance.ai_disclosure: true`.
3. **No misinformation.** Especially in health, finance, news, history. Keep claims accurate;
   add "not financial/medical advice" disclaimers (the system injects these for those niches).
4. **No impersonation / no real-person deepfakes** without consent. No cloning real voices.
5. **Licensed assets only.** Music = royalty-free/licensed (put your licensed tracks in
   `assets/music/`). Stock via Pexels/Pixabay is free for commercial use — keep attribution
   where their license asks. AI images: respect the model provider's commercial terms.
6. **No watermarks from other platforms** (also a quality/reach issue — see Playbook §4).

## Per-platform automation notes
- **YouTube:** API uploading is allowed. Don't artificially inflate views/subs. Shorts must be
  original to monetize; reused/repetitious content is demonetized.
- **TikTok:** Use the official **Content Posting API** (via aggregator). Disclose AI. Avoid
  banned-content categories. Don't run engagement bots.
- **Instagram/Facebook (Meta):** Use the **Graph API** (Reels). Business/Creator account
  required. Respect rate limits. Disclose AI-generated media.
- **All:** one human-owned account per channel; don't operate banned-region workarounds;
  don't mass-create accounts.

## Rate & posting hygiene
- 1–3 posts/day/account is well within limits. Don't burst 10+.
- Stagger posts; vary captions slightly per platform (the system does this).
- Keep a real profile: bio, picture, occasional reply to comments.

## Data & secrets
- All keys live in `.env` (git-ignored). Never commit secrets.
- Rotate tokens if a channel is sold or handed off.

## Disclaimers the system auto-injects (configurable in settings.yaml)
- Finance niches → "Not financial advice. For educational purposes only."
- Health niches → "Not medical advice. Consult a professional."
- AI disclosure line + platform synthetic-media flag when `ai_disclosure: true`.

> If a platform updates its policy, update `config/settings.yaml > compliance` and the
> niche disclaimers. Staying current is part of the daily/weekly operator job.
