# ArthMitra — Incident Response & DPDP Compliance Runbook

**Classification:** STRICT PRIVACY & INFRASTRUCTURE OPERATIONAL RUNBOOK  
**Applicability:** Production Operations, Security Incident Response, CERT-In & DPDP Act 2023 Compliance  

---

## 1. Statutory Breach Notification Timelines

Under Indian Law (DPDP Act 2023 & CERT-In Cyber Security Directions 2022):

| Regulator / Party | Mandatory Window | Contact / Portal | Required Information |
|---|---|---|---|
| **CERT-In** | **≤ 6 Hours** of noticing incident | incident@cert-in.org.in / +91-1800-11-4949 | Incident type, impacted systems, time of detection, containment steps taken |
| **Data Protection Board of India (DPB)** | **Promptly / Immediate** | dpb.gov.in electronic intimation | Nature of breach, volume of affected data principals, root cause, remedial actions |
| **Data Principals (Beneficiaries)** | Immediate post assessment | Direct SMS / Agent in-person intimation | Nature of breach, risks, protective steps taken, Grievance Officer contact |

---

## 2. Emergency Incident Classification

- **Severity 1 (Critical):** Data breach involving PII/phone numbers, unauthorized database export, key compromise, ransomware.
- **Severity 2 (High):** API unauthorized access, privilege escalation, abnormal token issuance rate.
- **Severity 3 (Medium):** Temporary service degradation, ASR/LLM external provider timeout, rate limit trip.

---

## 3. Immediate Severity 1 Containment Checklist

1. **Isolate Affected Pods/Servers:**
   ```bash
   # Terminate API ingress traffic immediately if active exfiltration detected
   docker compose down api worker
   ```
2. **Rotate Encryption Keys:**
   ```bash
   # Execute key rotation script with emergency newly generated key
   python scripts/rotate_encryption_key.py --old-key "$COMPROMISED_KEY" --new-key "$NEW_FERNET_KEY"
   ```
3. **Revoke Active JWT Sessions:**
   - Update `SECRET_KEY` in environment manager; all tokens immediately become invalid.
4. **Preserve Forensic Logs:**
   - Snapshot `audit_log` and `processing_log` tables before any database restructuring.
   - Extract reverse-proxy access logs.

---

## 4. Right-to-Erasure (DPDP Deletion) Workflow

When a beneficiary or Bank Sakhi requests deletion under DPDP Act:
1. Lodged via `POST /beneficiaries/{id}/deletion`.
2. Worker or administrator executes `POST /beneficiaries/{id}/execute-deletion`:
   - Beneficiary `first_name` overwritten with `"REDACTED"`, `deleted_at` set.
   - Consent audio object keys and audio hashes wiped.
   - All `CaseInput` records and LLM/voice transcripts deleted.
   - All generated DPR documents and Advisory outputs deleted.
   - `processing_log` entries are **strictly retained** for statutory 1-year compliance (contain only timestamps and purpose metadata, zero PII).
3. Confirm completion to the beneficiary.

---

## 5. Backup Restoration Procedure

1. **Verify Backup Integrity:**
   ```bash
   # Verify GPG / SHA256 checksum of daily backup
   sha256sum -c arthmitra_backup_20261027.sql.enc.sha256
   ```
2. **Restore Database:**
   ```bash
   pg_restore -h localhost -U postgres -d arthmitra -c -v arthmitra_backup_20261027.dump
   ```
3. **Verify Migrations:**
   ```bash
   alembic upgrade head
   ```

---

## 6. Grievance Redressal Officer Contact

- **Data Protection Officer (DPO):** privacy@arthmitra.org.in  
- **Escalation SLA:** Acknowledgment within 24 hours, resolution within 7 working days.
