# client-reels — branded 9:16 reels for clients

Client mode for Video_Autopilot. The parent pipeline makes faceless AI videos for
our own channels. This folder edits a **client's real footage** into on-brand Reels
(Remotion, React). Each reel renders with several hooks so the ad can be A/B tested.

```
src/clients/<client>.ts   brand kit + reels (hooks, scenes, CTA)  ← edit this
public/<client>/          the client's photos/clips, named per the shot list
out/<client>/             rendered MP4s: <reel>-<hook>.mp4
```

## Run

```bash
npm install
npm run render -- desi-meal            # every reel × hook  (~30s per reel on M-series)
npm run render -- desi-meal catering   # one reel
npm run studio                         # live preview / tweak timing in the browser
```

Output is 1080×1920 · 30fps · H.264 yuv420p (Meta-safe). Text stays inside the
Reels safe zone (clear of the top 260px, bottom 440px and the right action rail).
Remotion ships its own ffmpeg, so no Homebrew install is needed.

## Footage: how a stand-in becomes the real thing

Any scene whose file is missing renders as a branded stand-in that names the shot
it needs. Drop a file with the matching name into `public/<client>/` and re-render.
Video (`.mp4/.mov`) plays muted, full-bleed; stills (`.jpg/.png`) get a slow push-in.

### Desi Meal shot list (shoot vertical, daylight or warm light, 3–5s each)

| File | Shot |
|---|---|
| hook-desk.mp4 | Sad sandwich at a desk → push in |
| hook-tiffin.mp4 | Lid lifting off a steaming tiffin |
| hook-stack.mp4 | Stack of tiffins being packed |
| tiffin-1.mp4 | Curry being ladled, steam visible |
| tiffin-2.mp4 | Hands packing containers |
| tiffin-3.jpg | Full spread on the counter, top-down |
| tiffin-4.mp4 | Customer opening a tiffin at work |
| hook-trays.mp4 | Wide: catering trays lined up |
| hook-party.mp4 | Guests reaching for food, laughing |
| hook-buffet.mp4 | Slow pan across a full buffet |
| cater-1.mp4 | Phone typing a message (over-shoulder) |
| cater-2.mp4 | Chef plating several dishes |
| cater-3.mp4 | Trays loaded into the car / set on tables |
| cater-4.jpg | Hero shot of the full spread |
| hook-night.mp4 | Night exterior / sign lit up |
| hook-pour.mp4 | Slow-mo pour or tearing bread |
| hook-sizzle.mp4 | Tadka sizzle / flame |
| craving-1.mp4 | Tadka sizzle in a pan |
| craving-2.mp4 | Plate being finished, garnish dropped |
| craving-3.jpg | Counter / storefront, staff smiling |
| craving-4.mp4 | Bag handed over at the door |

## Before these run as paid ads

- **Audio:** reels render silent on purpose. Add trending audio inside Instagram
  when posting, or a track the client has a commercial licence for.
- **Facts:** copy uses only what the Desi Meal site states (halal, tiffin plans,
  3-step catering, delivery apps, open 7 days 12–9). Have the client approve it.
- **Handle:** set `brand.handle` once the Instagram handle is confirmed.
