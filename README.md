# Garcar Enablement System

Full-scale runtime that enables all built Garcar products and repos under the verified RHNS Kernel.

## What it is

- **Substrate**: the stdlib-only RHNS Kernel (planner, authority policy, idempotent ToolProxy, tiered Memory, Verifier, hash-chained Ledger). Tests pass.
- **Product registry**: RHNS-Architecture, apex-revenue-system, nwu-protocol, garcar-star, revenue-orchestrator, garcar-landing, BioForge Revenue organ.
- **Connector adapters**: safe stubs for GitHub issues, HubSpot notes, Stripe payment links (LLA-47 etc.), Gmail drafts, proof append. Swap for live clients.
- **Policy + Ledger**: every action is gated and hash-chained. EXTERNAL/FINANCIAL tools require explicit approval. No unauthorized sends or charges.
- **Walking skeleton**: list products → lookup → CRM note → prepare GitHub issue → proof append → (approval) draft email → (approval) prepare LLA-47 link.

## Run

```bash
python -c "from enablement import run_enablement; print(run_enablement('enable-1'))"
```

Ledger verifies. Policy holds. Products are registered and can be planned against.
