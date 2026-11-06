# Sources - Plex2Shell: Plex Media Server flaws exploited, QNAP NAS users report compromises

Primary
- QNAP security notice, "Plex Media Server vulnerabilities (Plex2Shell): update to 1.43.3.10861 or later immediately" (Nov 6, 2026): https://www.qnap.com/en/security-news/2026/qnap-security-notice-plex-media-server-vulnerabilities-plex2shell-update-to-1-43-3-10861-or-later-immediately - Plex Media Server 1.43.2 and earlier affected (CVE-2026-96652, -96654, -96655, -96656); QTS / QuTS hero not themselves affected; some users report Plex servers that appear compromised; compromised servers used to run cryptocurrency miners and proxy software; updating does not remove what an attacker installed; if Plex was internet-reachable on an old version treat the NAS as potentially compromised, clean reinstall, reset Plex and NAS credentials; disable Plex Remote Access, do not forward port 32400, use a VPN.
- CISA Known Exploited Vulnerabilities catalog - all four Plex2Shell CVEs added October 20, 2026 (reported by The Hacker News and BleepingComputer below).

Secondary
- BleepingComputer, "QNAP says hackers breaching NAS devices in Plex2Shell attacks" (Nov 6, 2026): https://www.bleepingcomputer.com/news/security/qnap-says-hackers-breaching-nas-devices-in-plex2shell-attacks
- BleepingComputer, "CISA: Hackers chain Plex flaws in Plex2Shell attacks to breach servers" (Oct 21, 2026): https://www.bleepingcomputer.com/news/security/cisa-hackers-chain-plex-flaws-in-plex2shell-attacks-to-breach-servers/ - chain gives the owner's admin token and code execution; researcher Zach Main; fixed in 1.43.3.10861.
- The Hacker News (Oct 2026): https://thehackernews.com/2026/10/cisa-orders-federal-agencies-to-patch.html - KEV addition Tuesday, October 20, 2026; researcher says the chain allows unauthenticated remote code execution; attackers deploy miners and proxy malware.

Notes
- Fix release date differs between sources (August 3 vs August 4, 2026), so the video does not state it.
- No exposed-server count is stated in the sources used, so the video gives none.
- Video says "run code on your server" attributed to the researcher, not "unauthenticated", to stay within what both secondary sources agree on.
- Analyst note ("a media server is still a computer on your home network, so patch it like one") is Securidge analysis.
