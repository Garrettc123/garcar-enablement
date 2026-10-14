# Garcar Enablement — Full Project

Unified stack that enables all built Garcar products under the RHNS Kernel, with an autonomous sales engine, agent layer, revenue layer, and key-once vault.

## Layers

| Layer | Path | Owns |
|---|---|---|
| RHNS Kernel | `rhns/` | planner, policy, ToolProxy, Memory, Verifier, Ledger |
| Enablement | `enablement.py` | product registry, LLMProposer, SKU surface |
| Connectors | `connectors/` | HubSpot, Notion, Linear, revenue spine stubs |
| Agent Layer | `agents/` | role registry, routing, bot handoff |
| Revenue Layer | `revenue/` | full SKU coverage, autokey, autonomy governor |
| Sales Engine | `garcar-autonomous-sales/` | Postgres, GAR-530 gate, Stripe, SMTP, ATLAS, portal |
| Key-Once Vault | `garcar-autonomous-sales/key_vault.py` | auto-mint internal secrets, HMAC only |

## Products enabled

RHNS-Architecture, apex-revenue-system, nwu-protocol, garcar-star, revenue-orchestrator, garcar-landing, BioForge Revenue.

## SKUs

LLA-47, AI-AUDIT-299, ENT-AUDIT-3500, MARS-750, MARS-1500, GROWTH-1497.

## Quick start

```bash
python main.py status
python main.py enable
python main.py agent --role research
python main.py revenue --sku LLA-47
cd garcar-autonomous-sales && python bootstrap.py
```

## Guards

- RHNS Policy holds EXTERNAL/FINANCIAL behind approval.
- GAR-530 gate: DNC, circuit breaker, confidence, leak floor, price lock.
- Key-once vault: raw key shown once, HMAC only on disk.
- Dual-ledger: estimate is intelligence; cash is Stripe paid=true last4≠4242.

## Tests

```bash
python -m unittest discover -s tests -v
```

All 11 tests pass.
