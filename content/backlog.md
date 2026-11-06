# Securidge content backlog

Prioritised topic list (KM, 2026-10-30). Scheduled runs read this when choosing a story — see RUNBOOK §3 step 2.
Rules:
- **Priority 1 (famous CVEs) comes first.** Pick the highest unused P1 item that fits the slot.
- Every item is a lead, not a script: re-open the sources, confirm every number/date, and add a
  second independent source (vendor advisory / CISA KEV / CERT) before using it.
- Status changes after these dates are possible (new patches, new exploitation) — check and say so.
- When an item is used, move it to **Done** with the video folder name. Never reuse a Done item
  unless there is genuinely new information (then title it "update:").
- Plain English: explain each CVE as "what can happen to you" + "what to do tonight".

## Priority 1 — recent well-known CVEs (explain simply)

| # | CVE | What it is (plain words) | Why viewers care | Best format | Status as of 2026-10-30 | Lead sources |
|---|---|---|---|---|---|---|

## Priority 2 — real scam cases that work as Shorts

| # | Case | Hook | Status / date | Lead sources |
|---|---|---|---|---|
| 9 | AI voice-clone "family emergency / kidnapping" calls | "It sounded exactly like my son" — set a family code word | Police warnings Jan–Jun 2026 (US, UK, India) | [Cleveland19](https://www.cleveland19.com/2026/01/23/ai-voice-cloning-scams-target-families-with-fake-kidnapping-calls/), [North Wales Police via Deeside](https://www.deeside.com/north-wales-police-warns-of-rise-in-deepfake-and-voice-cloning-scams/), [Tamil Nadu Police via Inc42](https://inc42.com/?p=454767) — avoid fear-mongering, cite real police advisories only |
| 10 | Fake QR codes on parking machines ("quishing") | The sticker over the real QR code | UK/German police warnings; a vendor reports a Q1 2026 surge (vendor figure — label it as such) | [Which?](https://www.which.co.uk/news/article/quishing-scams-warning-how-to-spot-and-avoid-dodgy-qr-codes-asYsH0h6jjP1), [Lee County Sheriff Apr 2026](https://www.sheriffleefl.org/?p=28573) |

## Priority 3 — evergreen Shorts (only with a fresh real example)

Public Wi-Fi risks · parcel-delivery smishing · passkeys explained · checking if your email leaked ·
"Mum, my phone broke" messenger scam · SMS vs authenticator-app 2FA (SIM swap) · app permissions ·
first hour of ransomware at work.

## Done

| Item | Video folder |
|---|---|
| Old iPhone zero-day | videos/2026-10-29-old-iphone-zero-day |
| Phishing red flags | videos/2026-10-29-phishing-red-flags |
| Calendar-invite phishing | videos/2026-10-30-am-calendar-invite-phishing |
| Authenticator CVE-2026-80097, So-net breach, Virtualine seizure | videos/2026-10-30-pm-week-authenticator-sonet-virtualine |
| Windows Shell MOTW bypass CVE-2026-96951 (P1 #1) | videos/2026-10-31-am-windows-warning-bypass |
| BeyondTrust Remote Support zero-day CVE-2026-102764 (P1 #4), Myth vs Fact | videos/2026-10-31-pm-beyondtrust-patch-myths |
| Apple CoreGraphics CVE-2026-86950 (P1 #2) — already covered by the Oct 26 older-iPhone backport video | videos/2026-10-29-old-iphone-zero-day |
| Chrome V8 zero-days CVE-2026-85046 (P1 #3) + newer CVE-2026-87491, "why Relaunch matters" | videos/2026-11-01-am-chrome-relaunch-zero-days |
| N-able N-central CVE-2026-86218 (P1 #5), Evergreen "one hacked IT tool, many hacked companies" | videos/2026-11-01-pm-it-provider-rmm-supply-chain |
| October 2026 Patch Tuesday size, 1,400+ flaws (P1 #6) — "why your Windows update is so big" | videos/2026-11-02-am-record-windows-update |
| 7-Zip XZ decoder CVE-2026-14266 (P1 #7) — "apps that never update themselves" | videos/2026-11-03-am-7zip-xz-update |
| Fake FBI IC3 "money recovery" scam (P2 #8) — PSA I-072026-PSA dated July 20, 2026 | videos/2026-11-07-am-fake-fbi-recovery-scam |
