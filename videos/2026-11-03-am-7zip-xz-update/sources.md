# Sources - 7-Zip XZ decoder flaw CVE-2026-14266

Primary
- ZDI-26-444 advisory, quoted on oss-security (Jul 17, 2026): https://www.openwall.com/lists/oss-security/2026/07/17/12 - heap-based buffer overflow in XZ chunked data; user must open a malicious file; CVSS 3.0 7.0; fixed in 7-Zip 26.02; reported Jun 5, 2026.
- CVE record (NVD/MITRE via OpenCVE): https://app.opencve.io/cve/CVE-2026-14266 - NVD CVSS 3.1 7.8 High; CNA ZDI; not in CISA KEV.

Secondary
- The Hacker News (Jul 20, 2026): https://thehackernews.com/2026/07/new-7-zip-vulnerability-could-let.html - 26.02 released Jun 25, 2026; no PoC or in-the-wild exploitation as of Jul 20; manual updates only; products bundling 7-Zip's XZ decoder need their own vendor fix.
- TechSpot: https://techspot.com/news/113175-7-zip-patches-flaw-could-run-malware-opening.html - no auto-update; install 26.02 manually.
- Rescana (backlog lead): https://www.rescana.com/post/cve-2026-14266-critical-7-zip-xz-archive-decoder-vulnerability-enables-remote-code-execution-patch-in-26-02

Wording notes: exploitation status stated as "as of the July reports, no attacks had been seen" (no newer report found on Nov 3, 2026).
