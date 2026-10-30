# Securidge production runbook

> 한국어 요약: 매일 05:00(쇼츠)·16:00(롱폼 16:9, 2분 30초 이내) 업로드용 영상을 만드는 절차서.
> 모든 사실은 1차 출처 포함 2곳 이상으로 검증, 모든 영상은 비공개로 업로드 → KM이 확인 후 공개.

Every scheduled run follows this file. Read it fully before starting. If anything here conflicts
with the task prompt, the task prompt wins.

## 0. Non-negotiables

1. **Private upload only.** Metricool `privacy: "private"`, `isAiGeneratedContent: true`,
   `madeForKids: false`. KM reviews in YouTube Studio and publishes himself.
2. **Every factual claim needs a source**, and the story needs at least two independent credible
   sources, at least one of them primary (vendor advisory, CISA / NCSC / CERT-In / ENISA notice,
   SEC filing, court record, the company's own statement, the paper itself).
   Keep hedges exactly as sourced: "may have been exploited", "claims", "reportedly".
   Attacker claims are never stated as fact. Numbers are copied, never rounded up.
3. **No fabricated experience.** The "Analyst note" is analysis (what this means, what to do),
   never an invented first-person anecdote. The AI voice never says "I worked at…".
4. **No AI persona giving legal, financial or medical advice.** Stay on security practice.
5. **Quotes under 15 words**, one per source; everything else in our own words.
6. If you cannot verify the story to this standard, pick another story. If nothing qualifies,
   make an evergreen explainer (section 2, "Evergreen") rather than publish something thin.
7. **Never repeat a topic** already in `videos/` unless there is a material new development
   (then say "update:" in the title).

## 1. Formats

| Slot (KST) | Format | Canvas | Spoken length | Scenes |
|---|---|---|---|---|
| 05:00 | YouTube Short (`format: "short"`, Metricool `type: "short"`) | 1080x1920 | 35–55 s (renderer rejects > 58 s) | 6–8 |
| 16:00 | Long-form (`format: "long"`, Metricool `type: "video"`) | 1920x1080 | 90–145 s (hard cap 150 s) | 9–14 |

Long-form must be 16:9: a vertical video under 3 minutes is filed by YouTube as a Short.

Shorts open with a **0.7-second** and long-form with a **1.5-second still, silent frame** (the renderer adds it; 1.5 s felt slow on Shorts — KM, 2026-10-30).
scene 1, so scene 1 must be a hook that works as a silent title card.

Audience: Europe, US, India. Use international English, explain US-only acronyms once
("the US agency CISA"), give dates as "October 26", avoid US-only references where a global one exists.

## 2. Editorial mix (rotate so consecutive videos never feel interchangeable)

Shorts (05:00): the single most actionable story of the last 72 hours for ordinary users or
employees — "what happened → why it matters → what to do tonight".

Long-form (16:00) by weekday (KST):
- Mon — **Breach Breakdown**: one real incident at a global company, timeline + root cause + lesson.
- Tue — **Patch & Exploit Watch**: the exploited bugs that matter this week (CISA KEV, vendor advisories).
- Wed — **Research Explained**: one peer-reviewed paper or major lab report (DOI / arXiv / official PDF),
  what it found, limits, what practitioners should do.
- Thu — **Company Case Study**: how a named global company handled a security decision
  (disclosure, ransom refusal, zero-trust rollout, outage post-mortem) using its own statements.
- Fri — **Week in Security**: 3–4 stories, each with its own source chip.
- Sat — **Myth vs Fact** explainer tied to a current story.
- Sun — **Evergreen** explainer (passkeys, MFA fatigue, NAC/zero trust, ransomware first hour…)
  anchored to a recent real example.

KM's own papers: use only if a published version with a DOI exists AND it is listed in
`research/approved.md`. Never use unpublished dissertation or in-review material.

## 3. Steps

1. **Repo**: `add_repo kkmkkmzz/securidge-media` with push access, then
   `git clone --depth 1 https://github.com/kkmkkmzz/securidge-media`. Read `videos/*/meta.json`
   titles to avoid repeats.
2. **Research** (WebSearch / WebFetch): first read `content/backlog.md` (KM's priority list —
   famous recent CVEs first). If a bigger, verified story broke in the last 72 h, it wins; otherwise
   take the highest unused backlog item that fits the slot, re-verify it, and move it to **Done** in
   the same commit. Then find candidates from the last 72 h (BleepingComputer,
   SecurityWeek, The Record, The Hacker News, Dark Reading, vendor blogs, CISA KEV, NCSC, CERT-In).
   Shortlist 3, pick the one with the best verification + relevance to EU/US/India viewers.
   Fetch the primary source and confirm every number/date you will say.
3. **Plan**: write `videos/<YYYY-MM-DD>-<slot>-<slug>/spec.json` (slot = `am` or `pm`).
   Scene kinds: `hook`, `point`, `stat`, `quote`, `timeline`, `steps`, `note`, `cta`.
   Every scene except hook/cta should carry `"source"` (short label). One `note` scene (Analyst note).
   `say` = exact narration for that scene. On-screen text must not contradict `say`.
   Hook rules: first sentence ≤ 10 words, concrete, names who is affected.
   **Motion (required quality bar — no static slideshow).** The renderer animates every scene on the
   narration's word timings: headlines type on with a cursor, `stat` numbers count up, `steps` and
   `timeline` items appear one by one (timeline gets a progress arrow from dot to dot), bodies fade in.
   **Focus effects — use sparingly (KM, 2026-10-30).** Built-in motion (headline typing, number
   count-up, items appearing as they are said) runs automatically. On top of that, choose focus
   effects only where a scene genuinely has one thing the viewer must not miss — most scenes get
   none. Budget: Shorts **2–3** per video, long-form **3–5**; never two in one scene; never on `cta`;
   do not use the same effect twice in a row.
   `"motion": {"fx": "<effect>", "target": "headline|body|big|item:N", "word": "<a word from say>"}`
   - `spotlight` — everything except the target dims; best for one step/item or the key line among several.
   - `color` — one spoken `word` inside the target turns accent colour the moment it is said; the
     word must appear in both `say` and the on-screen target text. Best for the single key term.
   - `pop` — a quick 0.4 s tap-scale of the target; best for a number or short verdict.
   - `push` — slow 4% camera push-in across the scene; best for the hook or a sober analyst note.
   - `zoom` — strong zoom into the target; at most once per video, only when it adds clarity.
   **Never draw** circles/rings, underlines or progress lines — they looked cheap; the renderer
   ignores them. For `steps`/`timeline` add `"item_words": ["<word>", ...]` (one spoken word per
   item) so each item appears as it is said.
4. **Voice**: ElevenLabs `creative_generate_speech`, model `eleven_v4`,
   voice **Pulse** `mhgBlD8CmCSdwLDOIJpA` (high-energy American male; do not change).
   Prompt = the `say` texts joined by blank lines, `[excited]` at the start, `[serious]` before the
   analyst note, `[excited]` before the final steps. Pass `generations_count: 1` (one take is enough
   and halves the credits). Poll until complete.
5. **Timing**: `creative_add_flow_asset_node` (audio, that generation_id) →
   `creative_transcribe_audio` (`eleven_scribe_v1`, connect_from = that node) → poll →
   download `words_download_url` to `words.json`; download the take to `narration.mp3`.
6. **Render**: `pip install --break-system-packages -q pycairo numpy` once, then
   `python3 tools/securidge_render.py spec.json narration.mp3 video.mp4 words.json`
   (motion lives in `tools/motion_fx.py`; `tools/reference/motion_demo.py` is only the approved look reference).
   It picks a fresh art style and logs it to `videos/styles_used.json`. A "WARN word mismatch"
   means `say` texts differ from what was spoken — fix the spec words (not the audio) and re-render.
7. **Look at it**: extract ~10 frames into a contact sheet and Read it. Check: nothing overflows,
   text readable on the background, captions match narration, source chips present, typing finished before the scene ends, nothing
   placed in the right 170 px or below y=1460 on Shorts. Fix the spec and re-render if needed.
8. **Archive**: `script.txt`, `sources.md`, `meta.json` (title ≤ 90 chars, description with every
   source URL + AI-voice disclosure, tags), then commit and push to `main`.
   **YouTube rejects `<` and `>` anywhere in the title or description** ("invalid video description").
   Write menu paths as "Settings, then General, then Software Update", never "Settings > General".
   Before scheduling, check: `grep -c '[<>]'` on the title and description must be 0.
9. **Schedule**: Metricool `createScheduledPost`, blogId `7715648`, timezone `Asia/Seoul`,
   media = `https://raw.githubusercontent.com/kkmkkmzz/securidge-media/main/videos/<folder>/video.mp4`,
   publication at the slot time (05:00 or 16:00 the same day). Long-form: add
   `videoCoverMilliseconds: 500` (the hook still); if rejected with VIDEO_THUMBNAIL_NOT_APPLICABLE,
   schedule again without it.
10. **Confirm upload**: about 5 minutes after the publication time, call getScheduledPosts for that
   window. If the YouTube provider status is ERROR, read detailedStatus, fix the cause, update the post
   with updateScheduledPost (providers youtube only, no twitterData/instagramData) and report it.
11. **Report**: send KM a short Korean message: title, topic, sources, style, Metricool planner link.
   If any step failed, do not schedule; say which step failed and why.
