# Garcar Enablement System — Full Stack

Full-scale runtime that enables all built Garcar products and repos under the verified RHNS Kernel.

## Stack layers

| Layer | Owns |
|---|---|
| RHNS Kernel | planner, policy, ToolProxy, Memory, Verifier, Ledger |
| Enablement | product registry, LLMProposer, SKU surface, approval gate |
| Connector Plane | GitHub, HubSpot, Stripe, Gmail, Notion, Linear (safe stubs → live) |
| BioForge Organs | Revenue spine (intake → fulfill), CRM, Outreach, Billing, Fulfillment |
| Operator Surface | CLI (`status`, `run`, `spine`, `products`, `skus`) |

## What is live

- Repo: https://github.com/Garrettc123/garcar-enablement
- Products: RHNS-Architecture, apex-revenue-system, nwu-protocol, garcar-star, revenue-orchestrator, garcar-landing, BioForge Revenue
- SKUs: LLA-47, AI-AUDIT-299, ENT-AUDIT-3500, MARS-750, MARS-1500, GROWTH-1497
- Policy holds EXTERNAL/FINANCIAL behind approval. Ledger verifies.

## Run

```bash
python cli.py status
python cli.py run --task full-1
python cli.py spine
```

## Revenue spine (BioForge)

lead_intake → enrich → outreach → proposal → checkout → crm_sync → fulfill → report

Outreach, checkout, crm_sync, and fulfill require approval (CMC commit). No silent money or reputation hops.
