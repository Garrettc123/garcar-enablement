# Agent layer

Role registry and task routing under the RHNS Kernel.

| Role | Purpose | Max authority |
|---|---|---|
| research | Lookup, enrich, briefs | REVERSIBLE |
| outreach | Draft consented messages | EXTERNAL (approval to send) |
| crm | Contact and deal notes | REVERSIBLE |
| billing | Prepare payment links | FINANCIAL (approval to charge) |
| governance | Plan, verify, audit | REVERSIBLE |
| fulfillment | Spine hops after paid=true | REVERSIBLE |

Handoff payloads for G / Os / Multiple Things. Does not send. Nothing sends, charges, or ships without approval.
