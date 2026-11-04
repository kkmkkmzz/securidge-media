# Sources - WordPress Core CVE-2026-119977 exploited (upgrade-window RCE)

Primary
- WordPress.org, "WordPress 7.1.4" (Oct 28, 2026): https://wordpress.org/news/2026/10/wordpress-7-1-4/ - fixes "a weakness in the WordPress upgrade process which can lead to remote code execution during the upgrade window"; 12 vulnerability fixes + 1 root certificate update; backports to branches "currently through 4.7"; sites with automatic background updates update automatically; "it is recommended that you update your sites immediately."
- CISA alert (Nov 3, 2026): https://www.cisa.gov/news-events/alerts/2026/11/03/cisa-adds-one-known-exploited-vulnerability-catalog - not fetchable this run (site error); content confirmed via BleepingComputer and The Hacker News.

Secondary
- BleepingComputer (Nov 4, 2026): https://www.bleepingcomputer.com/news/security/cisa-flags-wordpress-rce-flaw-as-actively-exploited-in-attacks/ - CISA added CVE-2026-119977 (TOCTOU race in core upgrade, predictable web-accessible staging paths, unauthenticated) to KEV on Nov 3; fixed in 7.1.4 (Oct 28); Wordfence blocked 13,095 attacks in 24 hours; federal deadline Nov 6.
- The Hacker News (Nov 4, 2026): https://thehackernews.com/2026/11/cisa-confirms-hackers-exploiting.html - same CVE, CVSS 8.1, KEV Nov 3, deadline Nov 6; Wordfence 18,500+ requests in first 21 h and 12,632 blocked in a 24 h window.

Not used: CVSS score in narration, exact affected-version range (Wordfence slug suggests 4.7-7.1.3, not confirmed in a fetched source), Previdian honeypot details (single source).
