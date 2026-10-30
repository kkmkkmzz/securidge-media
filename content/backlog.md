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
| 2 | CVE-2026-86950 (Apple CoreGraphics) | Opening a booby-trapped image/file can run code on iPhone/Mac | Hundreds of millions of Apple devices; "just an image" | Short | Exploited in targeted attacks; fixed iOS/iPadOS 26.7.1, macOS Tahoe 26.7.1, Sequoia 15.8.1 (Sep 28, 2026) | [BleepingComputer](https://www.bleepingcomputer.com/news/security/apple-patches-coregraphics-zero-day-flaw-exploited-in-attacks/amp/), Apple security release notes (confirm) |
| 3 | CVE-2026-85046 (Chrome V8) | Chrome's 6th exploited zero-day of 2026; a web page alone can trigger it | Billions of Chrome users; "why Chrome keeps asking you to restart" | Short | Fixed Chrome 152.0.7977.82/.83 (Sep 2026) | [eSecurity Planet](https://www.esecurityplanet.com/threats/news-google-chrome-cve-2026-85046-zero-day/), Chrome Releases blog (confirm) |
| 4 | CVE-2026-102764 (BeyondTrust Remote Support / PRA) | Auth bypass in an IT remote-support tool; spies used it as a front door | Business audience; the tool IT uses to help you was the way in | Long (Breach Breakdown / Company Case Study) | Exploited since late Aug 2026 by a suspected China-nexus group; patched Oct 2026 | [BleepingComputer](https://www.bleepingcomputer.com/news/security/beyondtrust-patches-zero-day-exploited-in-attacks-since-august/), BeyondTrust advisory, Mandiant (confirm) |
| 5 | CVE-2026-86218 (N-able N-Central, CVSS 9.8) | Unauthenticated remote code execution in software IT providers use to manage many companies at once | One hacked provider = many hacked customers (supply-chain idea, easy to visualise) | Long | Reported exploited; fixed in 2026.3.1.14; Singapore CSA alert Sep 9, 2026 | [CSA Singapore](https://www.csa.gov.sg/alerts-and-advisories/alerts/al-2026-118/), N-able advisory (confirm) |
| 6 | October 2026 Patch Tuesday size | Microsoft fixed a record 1,411 flaws in one month (70 critical) | Number hook for "why updates are so big" | Short | Oct 13, 2026 | [BleepingComputer on X](https://x.com/BleepinComputer/status/2110098145262899231), [Gadget Hacks](https://windows.gadgethacks.com/news/microsoft-patch-tuesday-october-2026-exploited-windows-flaw/) |
| 7 | CVE-2026-14266 (7-Zip XZ decoder) | Opening a crafted .xz archive could run code | Very popular free tool that never auto-updates | Short (evergreen: "update the apps that don't update themselves") | **Not** known exploited (as of Jul 20, 2026 report) — must say so; fixed in 7-Zip 26.02 | [Rescana](https://rescana.com/post/cve-2026-14266-critical-7-zip-xz-archive-decoder-vulnerability-enables-remote-code-execution-patch-in-26-02), 7-Zip changelog (confirm) |

## Priority 2 — real scam cases that work as Shorts

| # | Case | Hook | Status / date | Lead sources |
|---|---|---|---|---|
| 8 | Fake FBI IC3 "money recovery" scam | Scammers target people who were *already* scammed, promising to get their money back for a fee | FBI warning, Aug 19, 2026 | [WCAX](https://www.wcax.com/2026/08/19/fbi-warns-scammers-are-impersonating-its-cybercrime-complaint-center/), ic3.gov PSA (confirm) |
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
