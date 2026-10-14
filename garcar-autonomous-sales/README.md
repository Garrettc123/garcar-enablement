# Garcar Autonomous Sales — Production Package

Zero-mock production deployment for the autonomous sales loop.

## Architecture

```
garcar-autonomous-sales/
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── schema.sql
├── full_sales_engine.py
└── atlas_worker.py
```

## State machine

ATLAS Audit → Auto-Mint Approval → Stripe Session → Dispatch Pitch → Closer → Stripe Webhook (PAID) → Auto-Fulfill & Portal

## Guards (GAR-530)

- DNC / suppression list checked against PostgreSQL
- 24-hour outreach circuit breaker (default 250)
- Minimum confidence 0.85
- Minimum monthly leak $5,000
- Price locked to SKU catalog
- Outbound email requires AUTO-APR-* approval_id
- Stripe webhook is fail-closed (signature, amount, approval_id)

## Run

```bash
cd garcar-autonomous-sales
cp .env.example .env
docker compose up --build
```

Health: GET /health
Initiate: POST /api/v1/sales/initiate
Inbound: POST /api/v1/sales/inbound-reply
Webhook: POST /api/v1/billing/stripe-webhook
Portal: GET /portal/{lead_id}?token=...

Secrets stay on the host. Package dry-runs email and simulates checkout when absent.
