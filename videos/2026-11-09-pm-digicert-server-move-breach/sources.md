# Sources — 2026-11-09 PM (Breach Breakdown): DigiCert archived customer data exposed after a server move

Primary
- DigiCert, "DigiCert: Unauthorized access to business system", Mozilla Bugzilla bug 2084460 (self-reported; preliminary report 2026-10-20, full report as comment 2): https://bugzilla.mozilla.org/show_bug.cgi?id=2084460
  — 2025-02-04 migration from VPN-restricted segment to externally accessible zone; 2026-06-18 non-DigiCert accounts noticed, wrongly judged to have no data access; 2026-06-21 managed security program report; data access window 2026-06-27 to 2026-07-02; 2026-07-02 authorization patch; 2026-10-12 first suspicion of data access; 2026-10-19 reportable, window confirmed; root causes: change treated as infrastructure not security change, self-registration without MFA, unassigned accounts could read data, insufficient monitoring/alerting; data mostly names, business emails, phone numbers, business addresses, small minority with identity documents (driver's licence, passport, utility bill); "small proportion of archived data"; no record count; "No certificate operations were impacted."; reported to law enforcement (comment 7).

Secondary
- The Record (Nov 6, 2026): https://therecord.media/digicert-certificate-authority-reports-data-breach — spokesperson: reported to law enforcement; "no evidence of misuse of the information involved"; number affected not disclosed.
- The Register (Nov 6, 2026): https://www.theregister.com/security/2026/11/06/digicert-admits-16-month-security-lapse-exposed-customer-information/5308097 — "16-month security lapse"; CA operations, CertCentral, DigiCert ONE, credentials and certificates not affected.
- SecurityWeek (Nov 6, 2026): https://www.securityweek.com/digicert-data-breach-impacts-business-customer-information/ — data types; self-registration without MFA.
- Cyber Security News (Nov 5, 2026): https://cybersecuritynews.com/digicert-confirms-data-breach/ — customers do not need to replace active certificates.

Derived: "about sixteen months" = Feb 4, 2025 to Jun 18, 2026 (matches The Register's "16-month" framing).
Quote used (5 words): "No certificate operations were impacted." — DigiCert incident report.
Analyst note and the four lessons are Securidge analysis (lessons 1–3 echo DigiCert's own lessons learned).
