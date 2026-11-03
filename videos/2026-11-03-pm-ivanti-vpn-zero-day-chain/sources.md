# Sources - Ivanti Connect Secure zero-day chain (CVE-2026-104935, CVE-2026-111357, CVE-2026-118527)

Primary
- Canadian Centre for Cyber Security, Ivanti security advisory AV26-1035 (Oct 13, 2026; updated Oct 30, 2026): https://cyber.gc.ca/en/alerts-advisories/ivanti-security-advisory-av26-1035 - Connect Secure affected prior to 25.1.1.3, 25.1.3.1 and 22.8R2.6; CVE-2026-111357 exploited in the wild; CISA added CVE-2026-111357 and CVE-2026-118527 to KEV (update 2, Oct 30).
- Volexity, "A Series of Unauthenticated Events" (Oct 13, 2026; updated Oct 29, 2026): https://www.volexity.com/blog/2026/10/13/a-series-of-unauthenticated-events-chained-exploitation-of-ivanti-connect-secure-zero-days/ - exploitation began Oct 3; fully patched 22.8R2.4 compromised; chain = auth bypass + RCE (CVE-2026-104935) + privilege escalation to root (CVE-2026-111357); LDAP credentials taken; AD searched for LAPS passwords and BitLocker recovery keys; no web shell; logs edited; in-memory changes; Integrity Checker Tool did not detect it.
- Cyber Security Agency of Singapore alert AL-2026-147 (Oct 20, 2026; updated Nov 2): https://www.csa.gov.sg/alerts-and-advisories/alerts/al-2026-147/ - CVE-2026-104935 "reportedly being actively exploited".
- Ivanti advisory (could not be fetched this run; wording via Security Affairs): https://hub.ivanti.com/s/article/Security-Advisory-Ivanti-Connect-Secure-CVE-2026-104935?language=en_US

Secondary
- Help Net Security (Nov 2, 2026): https://www.helpnetsecurity.com/2026/11/02/cisa-to-federal-agencies-remediate-exploited-ivanti-connect-secure-vulnerabilities-cve-2026-111357-cve-2026-118527/ - three flaws exploited as zero-days together; CISA deadlines Nov 2 (with forensic triage) and Nov 13; preserve memory and logs; clean Integrity Checker result does not rule out compromise; rotate credentials.
- Security Affairs (Oct 31, 2026): https://securityaffairs.com/202175/security/u-s-cisa-adds-ivanti-connect-secure-flaws-to-its-known-exploited-vulnerabilities-catalog.html - KEV addition Oct 30; fixed versions 25.1.1.3 and 22.8R2.6; deadlines.
- Tech Insider (Nov 3, 2026): https://tech-insider.org/ivanti-connect-secure-cve-2026-111357-118527-kev-deadline-nov-13-2026/ - releases fixed for CVE-2026-104935 such as 22.8R2.5 remain vulnerable to the other two (consistent with Cyber Centre "prior to 22.8R2.6").

Not used: CVSS for CVE-2026-111357 (sources disagree: 8.8 per Ivanti vs lower per Rapid7/CVE record); patch date "Nov 2" reported by some trackers (Volexity dates the patch Oct 29); attribution beyond "UTA0576, previously unknown".
