# Sources - Synology NAS ransomware (C3RB3R / L0CK3D) on outdated DSM

Primary
- Synology press release, Oct 29, 2026, "Synology urges users to update DSM following ransomware attacks on outdated DSM versions": https://synology.com/en-global/company/news/article/C3RB3R - attackers "exploiting a vulnerability patched in December 2024" on outdated DSM; update DSM immediately; enable automatic updates; points to advisory Synology-SA-24:20.
- Synology security advisory Synology-SA-24:20: https://www.synology.com/zh-tw/security/advisory/Synology_SA_24_20 (referenced by Synology; not fetched this run).

Secondary
- BleepingComputer (Nov 2, 2026; updated Nov 3): https://bleepingcomputer.com/news/security/synology-warns-customers-of-ongoing-c3rb3r-ransomware-attacks - Shadowserver tracks 380,000+ internet-exposed Synology NAS (not all vulnerable/patched status unknown); files get ".L0CK3D", note "read-me3.txt"; victims reportedly asked for thousands of dollars; previous comparable Synology warning Aug 2019; advice: update DSM, auto-updates, block the management interface from the internet. Synology has not named the exploited flaw.
- IT-Connect (Oct 29, 2026): https://www.it-connect.tech/c3rb3r-ransomware-is-hitting-synology-nas-devices-how-to-protect-yours/ - RAID is not a backup; keep an offline copy; remove port forwards, use VPN.

Not used: specific fixed DSM build numbers (BleepingComputer table and IT-Connect list differ; IT-Connect also cites 2026 CVEs from a September advisory) and the 360 analysis details (single secondary source).
