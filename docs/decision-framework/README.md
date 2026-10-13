# Architecture Decisions & Business Value — Secure Enterprise RAG

**Status: Proposed decision guide, not an approved production architecture.**

Use the [reusable decision framework](https://github.com/mhartson310/Azure-Zero-Trust-Reference-Architectures/tree/main/docs/decision-framework/architecture-decision-framework), including the [ADR template](https://github.com/mhartson310/Azure-Zero-Trust-Reference-Architectures/tree/main/docs/decision-framework/architecture-decision-framework/ADR-template.md) and [business-case template](https://github.com/mhartson310/Azure-Zero-Trust-Reference-Architectures/tree/main/docs/decision-framework/architecture-decision-framework/business-case-template.md).

[Executive decision brief](../executive-decision-brief.md) · [Leadership threat-model summary](../threat-model-leadership-summary.md) ·

## Business objective and measurements

Help authorized employees retrieve and use enterprise knowledge without exposing documents they cannot access. Define source quality, answer relevance, privacy requirements, and expected organizational benefit before choosing an AI technology.

| Proposed KPI | Baseline to collect | Test before rollout |
|---|---|---|
| Task completion / time | Current manual workflow times | Controlled task comparison |
| Authorization leakage | Test corpus with explicit user-level ACLs | Zero unauthorized chunks reaching generation in test set |
| Answer relevance and citation grounding | Curated question/answer evaluation set | Agreed human-reviewed quality threshold |
| Operating cost | Retrieval, model, storage, ingestion, telemetry estimates | Cost per successful authorized answer at realistic scale |
| Operational health | Existing incident/availability data | Latency, failure rate and monitoring acceptance criteria |

## RAG-ADR-001 — Should the use case use AI at all?

**Options:** keep deterministic search/FAQ/workflow; augment with retrieval plus generation; automate through an agent.

**Trade-off:** Generative output may improve synthesis but adds probabilistic errors, sensitive-data risk, cost, evaluation overhead and ongoing monitoring.

**Decision gate:** A measurable user task benefits from generation beyond simpler search. If this cannot be shown in a pilot, choose the simpler approach.

## RAG-ADR-002 — RAG vs fine-tuning vs hybrid

**Options:** retrieval-grounded inference; fine-tuning for task/style or learned patterns; hybrid.

**Decision hypothesis:** For changing enterprise knowledge with per-user permissions and source attribution, prioritize permission-aware retrieval. Fine-tuning is not a replacement for document-level authorization or fresh source citations.

**Trade-offs:** retrieval adds index quality, ACL synchronization, freshness and query cost; fine-tuning adds data governance, training/evaluation, model versioning and potential memorization risks.

**Validation:** user-specific negative authorization tests, retrieval relevance, stale-document removal, citation correctness and inference quality.

## RAG-ADR-003 — Managed platform vs custom orchestration

**Options:** managed Azure services; custom retrieval/orchestration stack; managed/custom combination.

**Decision gates:** identity integration, private network support, audit/logging, portability, operations headcount, data residency, incident procedures and lifecycle support.

**Trade-off:** managed services can reduce infrastructure operations; custom control may improve specialized behavior but increases maintenance, security and upgrade burden. Validate with dated implementation and run-cost assumptions.

## RAG-ADR-004 — Model and vendor selection

Compare candidates based on an actual benchmark rather than a generic leaderboard:

| Dimension | Evidence needed |
|---|---|
| Quality | Representative prompts, held-out answers and human-reviewed rubric |
| Safety | Prompt-injection, indirect injection and sensitive-data exposure tests |
| Data handling | Residency, retention, contractual conditions, training use, subprocessors |
| Cost | Model input/output tokens, cached usage, embedding, retrieval, tool calls |
| Performance | p50/p95 latency, rate limits, resiliency and availability by region |
| Operational fit | Deployment, versions, observability, fallback, governance and exit path |

**Do not name a universal winner:** vendor features, pricing and availability change, and no environment-specific benchmark has yet been recorded.

## Governance and cost gates

- Source permissions must be enforced **before** chunks reach the model; validate ACL synchronization and security trimming.
- Treat retrieved documents as untrusted content.
- Include data classification, retention, prompt/log handling, tenant isolation, Private Link and managed identity assumptions.
- Model TCO includes ingestion, storage, retrieval, inference, evaluation, security telemetry, human review and operational support.

## Evidence and implementation links

[Architecture](../../architecture/README.md) · [Threat model](../threat-model.md) · [Security controls](../security-controls.md) · [Validation checklist](../validation-checklist.md) · [Tests](../../tests)

**Evidence status:** repository design and tests are reviewable; no measured production ROI, universal vendor recommendation or live enterprise rollout is claimed.
