# Sources — Chrome exploited zero-days 2026 (CVE-2026-87491, CVE-2026-85046)

Primary
- Canadian Centre for Cyber Security, AV26-904 (Sep 9, 2026): Chrome prior to 153.0.8010.37 affected; quotes Google "Google is aware that an exploit for CVE-2026-87491 exists in the wild"; CISA added it to KEV on Sep 9, 2026: https://cyber.gc.ca/en/alerts-advisories/google-security-advisory-av26-904
- NVD description (via The Hacker News): "allowed a remote attacker to execute arbitrary code inside the sandbox via a crafted HTML page"
- Chrome Releases blog (index checked; current stable 156.0.8078.79/.80 on Oct 29, 2026): https://chromereleases.googleblog.com/2026/?hl=en

Secondary
- Security Affairs (Sep 9, 2026): out-of-bounds write in V8; fixed 153.0.8010.36/.37; reported 2026-08-06 by Jihyeon Jeong (Seoul National University); seventh exploited Chrome zero-day of 2026 (lists all seven): https://securityaffairs.com/198757/security/google-fixes-the-seventh-actively-exploited-chrome-zero-day-of-2026.html
- Security Affairs (Sep 10, 2026): CISA KEV addition; federal deadline Sep 12, 2026: https://securityaffairs.com/198850/security/u-s-cisa-adds-cisco-google-chromium-v8-fortinet-and-citrix-netscaler-flaws-to-its-known-exploited-vulnerabilities-catalog.html
- The Hacker News (Sep 9, 2026): seven exploited Chrome zero-days in 2026; Edge, Brave, Opera, Vivaldi users should apply vendor fixes: https://thehackernews.com/2026/09/chrome-v8-zero-day-exploited-in-wild.html
- Help Net Security (Sep 4, 2026): CVE-2026-85046 (backlog lead), V8 type confusion, sixth zero-day, fixed 152.0.7977.82/.83: https://www.helpnetsecurity.com/2026/09/04/google-chrome-zero-day-cve-2026-85046/

Not used on purpose: severity score (Chromium rates it medium; CVSS 8.8 per Security Affairs — conflicting framing); "seven" said as "at least seven" because counts are as of Sep 9, 2026 and no later 2026 exploited Chrome zero-day was found.
