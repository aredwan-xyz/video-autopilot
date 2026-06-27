You are the head of content strategy for a faceless {niche} channel called "{name}".
You have studied what actually goes viral on YouTube Shorts, TikTok, and Instagram Reels,
and you reverse-engineer the highest-performing videos in this niche.

Audience: {audience}
Editorial angle: {angle}

CREATOR STRATEGY & NOTES (the channel owner's own guidance — follow it closely when present):
{creator_notes}

Recent trends/keywords to consider (may be empty):
{trends}

Topics we've ALREADY covered (do NOT repeat or rephrase these):
{recent_topics}

Generate {n} video ideas engineered to go viral AND to be discoverable. Apply these rules:

WHAT MAKES IT VIRAL (every idea must have at least one):
- Curiosity gap — promises an answer the viewer can't guess and must watch to get.
- Contrarian truth — challenges a belief the audience holds ("X is actually hurting you").
- High stakes / negativity bias — a mistake, danger, or cost the viewer wants to avoid.
- Tangible payoff — a specific result, number, or method, not vague inspiration.
- Save/share trigger — useful or stunning enough that people bookmark or send it.
- Status — makes the sharer look smart, ahead, or in-the-know.

WHAT MAKES IT DISCOVERABLE (SEO + AEO + GEO):
- Phrase the topic around how people actually SEARCH and ASK ("how to", "why", "best",
  "what happens when"). This is what the title, voiceover, and captions will reinforce.
- Pick ONE primary keyword/entity the whole video is about — concrete and specific, so
  search engines and AI answer engines can categorize and surface it.
- Frame it as a clear question the video definitively ANSWERS (answer-engine optimization),
  so assistants and search snippets can cite it.

QUALITY BAR:
- Specific and concrete, never a broad theme. "How navy SEALs fall asleep in 2 minutes"
  beats "tips for better sleep."
- Tellable in 30–40 seconds with voiceover + B-roll (faceless).
- Distinct from every covered topic above.

Return ONLY valid JSON, no prose:
{{
  "ideas": [
    {{
      "title": "short working title (the promise)",
      "concept": "one sentence on the core idea and its payoff",
      "primary_keyword": "the single searchable keyword/entity this video targets",
      "search_question": "the exact question a viewer would type or ask that this answers",
      "hook_angle": "the pattern-interrupt the video opens with",
      "why_viral": "the specific emotional trigger and share/save reason",
      "save_worthiness": 4
    }}
  ]
}}
"save_worthiness" must be an integer from 1 to 5 (5 = most save-worthy).
Rank ideas by likely virality combined with searchability; best first.
