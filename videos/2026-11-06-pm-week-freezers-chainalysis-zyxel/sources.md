# Sources — Week in Security, 2026-11-06

## Story 1 — Cold-chain / freezer attacks
- PRIMARY: CISA, FBI, HHS, USDA, DOT joint fact sheet, Nov 5 2026 — https://www.cisa.gov/news-events/news/cisa-fbi-hhs-usda-and-dot-urge-critical-infrastructure-strengthen-industrial-refrigeration-and-cold (PDF: https://www.cisa.gov/sites/default/files/2026-11/joint-factsheet-usg-partners-urge-hardening-industrial-refrigeration-cold-chain-monitoring-systems-508c.pdf). cisa.gov blocked fetch; contents confirmed by the three outlets below.
- BleepingComputer, Nov 5 — five agencies; 115+ stores in six countries, up to 50°C; EFS confirmed Nov 3, three sites. https://www.bleepingcomputer.com/news/security/fbi-cisa-warn-of-cyberattacks-targeting-refrigeration-systems/
- The Register, Nov 5 — advisory recommendations; Delhaize stores hit. https://www.theregister.com/security/2026/11/05/feds-warn-grocers-dont-chill-on-cyber-defenses-as-freezer-hacking-spree-heats-up/5307978
- TechCrunch, Nov 5 — joint statement, Butera quote. https://techcrunch.com/2026/11/05/u-s-government-warns-of-ongoing-cyber-threat-amid-mass-hacks-of-industrial-retail-and-military-freezers/
- SecurityWeek / AP, Nov 5 — EFS statement: "no blood products were lost"; supplier Coolworld. https://www.securityweek.com/cyberattack-hits-french-blood-bank-site-but-no-blood-products-are-compromised/

## Story 2 — Chainalysis
- PRIMARY: Chainalysis, "Updated Nov 4: Chainalysis Security Incident Information" — https://www.chainalysis.com/blog/security-incident-october-30/ (Oct 30 no credentials/tokens; Nov 2 Reactor + Data Solutions offline; Nov 4 9:50 ET subset of passwords via on-path attack; Nov 4 11 PM ET names, usernames, password hashes, live tokens for all users; reset password + rotate API keys via login page)
- The Record — https://therecord.media/chainalysis-all-users-hit-by-agentic-cyberattack

## Story 3 — Zyxel GS1900 CVE-2026-107441
- PRIMARY: Zyxel CNA CVE record (CVSS 8.8, AV:A, OOB write in CGI, OS command execution, 10 models, published Nov 3) — https://app.opencve.io/cve/CVE-2026-107441 ; Zyxel advisory https://www.zyxel.com/global/en/support/security-advisories/zyxel-security-advisory-for-out-of-bounds-write-vulnerability-in-gs1900-series-switches-11-03-2026
- SecurityWeek, Nov 5 — almost 1,000 devices, blamed on CVE-2026-7273 (fixed June), Binarly found new zero-day; fixes Oct 23, advisory Nov 3. https://www.securityweek.com/zyxel-switch-hacks-blamed-on-patched-flaw-actually-exploited-a-zero-day/
