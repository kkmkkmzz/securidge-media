# Sources - "Poisoned Source": outdated iPhones and Android phones attacked through websites

Primary
- Sekoia TDR, "Poisoned Source: APT29 watering holes target mobile devices with n-day exploits" (Nov 4, 2026): https://www.sekoia.com/blog/poisoned-source-apt29-watering-holes-targets-mobile-devices-with-n-day-exploits - "we assess with moderate to high confidence that this campaign was conducted by APT29"; iOS 16.7 chain (cookies), iOS 18.5 DarkSword chain (full device data: messages, Keychain, Wi-Fi keys, photos...), Android Chrome 139-145 except 143 (cookies, login data, history, Wi-Fi config); Plerdy tracker compromised 27 August - 3 September 2026; "All three exploit chains rely entirely on known, already-patched vulnerabilities"; "a user running an up-to-date operating system is safe from these attacks."
- CISA KEV alert (Nov 4, 2026): https://www.cisa.gov/news-events/alerts/2026/11/04/cisa-adds-one-known-exploited-vulnerability-catalog - could not be fetched this run (permission timeout); KEV addition of CVE-2024-27834 on Nov 4 with Nov 18 deadline confirmed via The Hacker News and CybelAngel.

Secondary
- The Hacker News (Nov 5, 2026): https://thehackernews.com/2026/11/hackers-exploit-patched-apple-flaw-to.html - CVE-2024-27834 added to KEV Nov 4, deadline Nov 18; Apple fixed it May 2024 (iOS 17.5 / 16.7.8, macOS Sonoma 14.5, Safari 17.5).
- The Hacker News (Nov 4, 2026): https://thehackernews.com/2026/11/apt29-linked-hackers-hijack-web.html - campaign details, compromised sites, lookalike domains, Plerdy (Ukrainian web analytics service).
- CybelAngel (Nov 5, 2026): https://cybelangel.com/blog/apt29-plerdy-analytics-script-mobile-exploits/ - same facts; notes "CISA and Apple have not attributed the activity."

Hedges kept: attribution is Sekoia's ("links", "moderate to high confidence"); Sekoia says it is unclear whether specific visitors were targeted, so the video does not claim mass infection.
Not used: names of compromised sites, CVE list beyond CVE-2024-27834, exfiltration server.
