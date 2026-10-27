# ArthMitra — Blue/Green Deployment & Rollback Runbook

**Document Version:** 1.0.0  
**Effective Date:** October 2026  
**Audience:** Platform Engineering, DevOps, Lead Developers, SRE  
**Target Infrastructure:** AWS India Region (`ap-south-1` Mumbai)  
**Compliance Standards:** DPDP Act 2023 (Data Localization & Security Safeguards), OWASP ASVS L2

---

## 1. Architecture & Principles

ArthMitra operates on an active-active or blue/green architecture in AWS `ap-south-1` (Mumbai) to ensure zero downtime and strict adherence to statutory data residency.

```
       Internet / CloudFront (India PoPs)
                      │
                      ▼
       Application Load Balancer (ALB)
            │                  │
   [Target Group A]     [Target Group B]
     (Green - New)       (Blue - Current)
            │                  │
      ECS Fargate         ECS Fargate
      FastAPI API         FastAPI API
            └─────────┬────────┘
                      ▼
     ┌─────────────────────────────────┐
     │ RDS PostgreSQL 16 + PostGIS DB  │ (Multi-AZ, Encrypted)
     │ ElastiCache Redis 7 Cluster     │ (Queue & Cache)
     │ S3 Bucket (AES-256 SSE)         │ (DPR & Consent Media)
     └─────────────────────────────────┘
```

### Core Deployment Principles
1. **Zero Downtime**: Active field agents completing micro-enterprise intakes or consent recordings must never experience dropped sessions or 500 errors.
2. **Expand-Contract Database Migrations**: Schema alterations must remain strictly backwards-compatible with the active running version. Never drop or rename columns in the same release as new code.
3. **Automated Health Gate**: New task definitions only receive live traffic once `/health` and deep readiness checks return HTTP 200 for 3 consecutive polls (interval: 10s).
4. **Instant Rollback**: If p95 latency spikes > 800ms or 5xx error rate > 0.5% during canary shift, traffic is instantly swung back to Blue.

---

## 2. Pre-Deployment Gating

Before initiating any deployment to staging or production, verify all mandatory checks pass in CI:

```bash
# 1. Run all backend tests (rules, finance, viability, privacy, APIs)
pytest arthmitra/backend/tests -v

# 2. Run all frontend tests & production build (Strict budget: <= 500 kB gzipped)
npm --prefix arthmitra/frontend test
npm --prefix arthmitra/frontend run build

# 3. Verify static code quality & types
ruff check arthmitra/backend
mypy arthmitra/backend/engines
npm --prefix arthmitra/frontend run lint

# 4. Secrets scanning (ensure no AWS/API keys or PII)
git diff HEAD~1 | grep -E "AKIA[0-9A-Z]{16}|secret|password" || true
```

---

## 3. Step-by-Step Blue/Green Deployment Procedure

### Step 1: Database Migration (Expand Phase)
Migrations must be executed prior to container traffic switch and must only add nullable columns, new tables, or non-destructive indexes.

```bash
# Connect via AWS SSM / Bastion to ECS task or maintenance runner
export DATABASE_URL="postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/arthmitra"

# Run alembic upgrade to target head
cd /app/backend
alembic upgrade head

# Verify current revision matches repository HEAD
alembic current
```

### Step 2: Build & Tag Container Images
Images must be tagged with the exact git commit SHA and immutable release version.

```bash
GIT_SHA=$(git rev-parse --short HEAD)
AWS_ACCOUNT_ID="123456789012"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.ap-south-1.amazonaws.com"

# Build FastAPI API image
docker build -t ${ECR_REGISTRY}/arthmitra-api:${GIT_SHA} -f backend/Dockerfile .
docker push ${ECR_REGISTRY}/arthmitra-api:${GIT_SHA}

# Build RQ Background Worker image
docker build -t ${ECR_REGISTRY}/arthmitra-worker:${GIT_SHA} -f backend/Dockerfile.worker .
docker push ${ECR_REGISTRY}/arthmitra-worker:${GIT_SHA}

# Build Frontend PWA Static Assets (deployed to S3 + CloudFront)
npm --prefix frontend run build
aws s3 sync frontend/dist/ s3://arthmitra-${ENV}-static-web-in/ --delete
aws cloudfront create-invalidation --distribution-id ${CF_DIST_ID} --paths "/*"
```

### Step 3: Register New ECS Task Definition & Deploy Green
Update the ECS service task definition with the new image SHA:

```bash
# Update task definition with new image tag
TASK_DEF_ARN=$(aws ecs register-task-definition \
  --family arthmitra-${ENV}-api \
  --cli-input-json file://infra/ecs/api-task-def.json \
  --query 'taskDefinition.taskDefinitionArn' \
  --output text)

# Deploy to Green Target Group
aws ecs update-service \
  --cluster arthmitra-${ENV}-cluster \
  --service arthmitra-${ENV}-api-green \
  --task-definition ${TASK_DEF_ARN} \
  --force-new-deployment
```

### Step 4: Health Check Gating & Readiness Verification
Before shifting load balancer traffic, verify container health:

```bash
# Probe internal Green service ALB health endpoint
GREEN_IP=$(aws ecs list-tasks --cluster arthmitra-${ENV}-cluster --service arthmitra-${ENV}-api-green ...)
curl -s -f http://${GREEN_IP}:8000/health | jq .

# Expected output:
# {
#   "status": "ok",
#   "environment": "production",
#   "database": "connected",
#   "redis": "connected",
#   "timestamp": "2026-10-27T12:00:00Z"
# }
```

### Step 5: Traffic Shifting (Canary & Cutover)
1. Route 10% of traffic to Green for 5 minutes.
2. Monitor CloudWatch Alarms:
   - TargetResponseTime p95 ≤ 800ms
   - HTTPCode_Target_5XX_Count == 0
   - Redis queue depth for DPR jobs ≤ 10
3. If stable, shift 100% of traffic to Green.
4. Keep Blue instances warm in standby for 30 minutes.

---

## 4. Rollback Procedures

### Trigger Conditions for Immediate Rollback
- CloudWatch Alarm: `High5xxRate` (> 0.5% over 2 minutes).
- Latency spike: `/cases/{id}/evaluate` p95 > 1,500ms.
- Worker failures: DPR PDF generation failures on Redis queue > 1%.
- DB deadlock or migration runtime locks detected.

### Fast Traffic Rollback (< 60 Seconds)
Instantly swing ALB routing weight back to 100% Blue:

```bash
# Set ALB listener rule back to 100% Blue Target Group
aws elbv2 modify-listener \
  --listener-arn ${ALB_LISTENER_ARN} \
  --default-actions Type=forward,TargetGroupArn=${BLUE_TARGET_GROUP_ARN}

echo "Traffic restored to Blue. Green isolated for investigation."
```

### ECS Service Rollback
Revert the ECS service to the previously stable Task Definition revision:

```bash
aws ecs update-service \
  --cluster arthmitra-${ENV}-cluster \
  --service arthmitra-${ENV}-api \
  --task-definition arthmitra-${ENV}-api:${PREVIOUS_STABLE_REVISION} \
  --force-new-deployment
```

### Database Migration Rollback (Contract Phase)
Because migrations strictly follow expand-contract, rollbacks do not require immediate `downgrade` unless a corrupt constraint was created.
If manual downgrade is necessary:

```bash
# Revert single migration step
alembic downgrade -1
```

---

## 5. Post-Deployment Verification Checklist

- [ ] `/health` endpoint returns `200 OK` with DB and Redis connected.
- [ ] Field Agent login flow works (`POST /auth/login`).
- [ ] Beneficiary voice consent recording persists to encrypted S3 and creates audit ledger entry.
- [ ] Evaluation endpoint returns top-3 financing packages within ≤ 800ms.
- [ ] DPR PDF generation generates valid 12-section bilingual PDF in S3 within ≤ 3.0s.
- [ ] Supervisor dashboard displays real-time case aggregates and saturation metrics.
- [ ] CloudWatch error metrics remain at 0.
