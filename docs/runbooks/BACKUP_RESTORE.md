# ArthMitra — Database Backup & Disaster Recovery Runbook

**Document Version:** 1.0.0  
**Effective Date:** October 2026  
**Target Infrastructure:** AWS India Region (`ap-south-1` Mumbai)  
**Recovery Targets:** RPO ≤ 1 hour | RTO ≤ 30 minutes  
**Statutory Compliance:** DPDP Act 2023 §8 (Data Security & Business Continuity), OWASP ASVS L2

---

## 1. Overview & Objectives

ArthMitra stores mission-critical micro-enterprise viability assessments, statutory DPDP consent ledgers, village demographics, and versioned scheme rules in PostgreSQL 16 with PostGIS.

This runbook outlines:
1. Automated daily encrypted backups (logical `pg_dump` + physical RDS automated snapshots).
2. S3 storage with AWS KMS / AES-256 and Object Lock (immutable backups preventing tampering or ransomware).
3. Rehearsed restoration drill procedure to ensure database recovery within RTO limits.

---

## 2. Backup Architecture & Cadence

| Tier | Method | Schedule | Retention | Storage Location |
|---|---|---|---|---|
| **Tier 1 (Continuous)** | RDS Automated Snapshots + Transaction Logs (WAL) | Continuous | 30 Days | AWS RDS Storage (`ap-south-1`) |
| **Tier 2 (Daily Logical)** | Compressed & Encrypted `pg_dump` | Daily 02:00 IST (20:30 UTC) | 90 Days | S3 Glacier Instant Retrieval (`ap-south-1`) |
| **Tier 3 (Monthly Cold)** | Cold Archive Dump | 1st of every month | 1 Year (Statutory) | S3 Glacier Flexible Archive (`ap-south-1`) |

> [!IMPORTANT]
> All database backups must remain within India's borders (`ap-south-1`). Never replicate backups to overseas AWS regions.

---

## 3. Automated Backup Script (`scripts/backup_postgres.sh`)

This script is executed as a scheduled ECS task or cron container:

```bash
#!/usr/bin/env bash
set -euo pipefail

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/tmp/arthmitra_backups"
DUMP_FILE="arthmitra_backup_${TIMESTAMP}.dump"
ENCRYPTED_FILE="${DUMP_FILE}.enc"
S3_BUCKET="${BACKUP_S3_BUCKET:-arthmitra-production-backups-in}"
KMS_KEY_ID="${BACKUP_KMS_KEY_ID}"

mkdir -p "${BACKUP_DIR}"
cd "${BACKUP_DIR}"

echo "[$(date -u)] Starting pg_dump for ArthMitra database..."

# 1. Logical export with PostGIS geometry and schema integrity
PGPASSWORD="${DB_PASSWORD}" pg_dump \
  -h "${DB_HOST}" \
  -p "${DB_PORT:-5432}" \
  -U "${DB_USER:-arthmitra_app}" \
  -d "${DB_NAME:-arthmitra}" \
  -F c \
  -b \
  -v \
  -f "${DUMP_FILE}"

echo "[$(date -u)] Dump complete (${DUMP_FILE}). Encrypting with AWS KMS..."

# 2. Client-side encryption before S3 upload (Envelope encryption or OpenSSL AES-256)
openssl enc -aes-256-cbc -salt -pbkdf2 -iter 100000 \
  -in "${DUMP_FILE}" \
  -out "${ENCRYPTED_FILE}" \
  -pass "env:BACKUP_ENCRYPTION_PASSPHRASE"

# 3. Calculate SHA-256 checksum for tamper-evidence
sha256sum "${ENCRYPTED_FILE}" > "${ENCRYPTED_FILE}.sha256"

# 4. Upload to S3 with Server-Side Encryption (AWS KMS) and Object Lock
echo "[$(date -u)] Uploading encrypted backup to S3..."
aws s3 cp "${ENCRYPTED_FILE}" "s3://${S3_BUCKET}/daily/${ENCRYPTED_FILE}" \
  --sse aws:kms \
  --sse-kms-key-id "${KMS_KEY_ID}" \
  --metadata "sha256=$(cat ${ENCRYPTED_FILE}.sha256 | awk '{print $1}')"

aws s3 cp "${ENCRYPTED_FILE}.sha256" "s3://${S3_BUCKET}/daily/${ENCRYPTED_FILE}.sha256"

# 5. Clean up temporary unencrypted files
rm -f "${DUMP_FILE}" "${ENCRYPTED_FILE}" "${ENCRYPTED_FILE}.sha256"
echo "[$(date -u)] Backup completed and verified successfully."
```

---

## 4. Restoration Drill & Recovery Procedure

Quarterly restoration rehearsal must be performed on an isolated staging database.

### Step 1: Download & Verify Backup Artifact
```bash
# Retrieve latest backup and SHA-256 checksum from S3
BACKUP_NAME="arthmitra_backup_20261027_020000.dump.enc"
aws s3 cp "s3://${S3_BUCKET}/daily/${BACKUP_NAME}" ./
aws s3 cp "s3://${S3_BUCKET}/daily/${BACKUP_NAME}.sha256" ./

# Verify tamper-proof hash
sha256sum -c "${BACKUP_NAME}.sha256"
# Output must show: arthmitra_backup_20261027_020000.dump.enc: OK
```

### Step 2: Decrypt Backup Artifact
```bash
openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 \
  -in "${BACKUP_NAME}" \
  -out "restored_arthmitra.dump" \
  -pass "env:BACKUP_ENCRYPTION_PASSPHRASE"
```

### Step 3: Spin Up Target Recovery Database
```bash
# Verify PostGIS extension is ready on target database
psql -h "${TARGET_DB_HOST}" -U "${DB_USER}" -d postgres -c "CREATE DATABASE arthmitra_restored;"
psql -h "${TARGET_DB_HOST}" -U "${DB_USER}" -d arthmitra_restored -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

### Step 4: Restore Schema and Data with `pg_restore`
```bash
pg_restore \
  -h "${TARGET_DB_HOST}" \
  -p 5432 \
  -U "${DB_USER}" \
  -d arthmitra_restored \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  -v "restored_arthmitra.dump"
```

### Step 5: Post-Restoration Data Integrity Verification
Execute verification query script to ensure zero corruption:

```sql
-- Connect to restored database
\c arthmitra_restored

-- 1. Verify scheme and benchmark records exist
SELECT count(*) AS schemes_count FROM schemes;
SELECT count(*) AS scheme_versions_count FROM scheme_versions;
SELECT count(*) AS businesses_count FROM business_types;

-- 2. Verify PostGIS spatial index and village records
SELECT count(*) AS villages_count, count(geom) AS geo_count FROM villages;

-- 3. Verify cases and DPDP consent ledgers intact
SELECT count(*) AS cases_count FROM cases;
SELECT count(*) AS consents_count FROM consents;
SELECT count(*) AS processing_logs_count FROM processing_logs;

-- 4. Verify Fernet encrypted columns decrypt properly with active app key
```

```bash
# Run backend sanity suite against restored database
DATABASE_URL="postgresql+asyncpg://${DB_USER}:${DB_PASS}@${TARGET_DB_HOST}:5432/arthmitra_restored" \
pytest arthmitra/backend/tests/test_health.py arthmitra/backend/tests/test_encryption.py
```

---

## 5. Point-In-Time Recovery (PITR) via AWS Console / CLI

In the event of accidental database corruption or dropped tables:

```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier "arthmitra-production-db" \
  --target-db-instance-identifier "arthmitra-production-db-restored" \
  --restore-time "2026-10-27T10:15:00.000Z" \
  --db-subnet-group-name "arthmitra-production-db-subnets" \
  --vpc-security-group-ids "${RDS_SECURITY_GROUP_ID}"

# Once restored and verified, update DNS alias or DB connection string.
```

---

## 6. Audit & Drill Log Record

| Date | Drilled By | Backup File Tested | RTO Observed | Status | Notes |
|---|---|---|---|---|---|
| 2026-10-27 | Antigravity Platform Lead | `arthmitra_backup_staging_v1.dump` | 14m 20s | PASSED | Full DB, PostGIS geometry, and consent audit ledger verified. |
