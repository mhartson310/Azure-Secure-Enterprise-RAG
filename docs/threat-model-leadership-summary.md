# Leadership Threat Model Summary — Secure Enterprise RAG on Azure

**System:** Enterprise knowledge retrieval and grounded AI responses on Azure  
**Prepared for:** AI and security leadership, enterprise data owners, and risk/budget sponsors  
**Assessment status:** DESIGN/TEST-ARTIFACT LEVEL — no verified enterprise production deployment  
**Confidence:** High that the threat *categories* merit testing; **unverified** effectiveness in a live deployment

## 1. What Would Someone Want From Us?

- **Confidential enterprise documents:** content that a requester is not authorized to access, including information carried through search results, prompts, responses, or logs.
- **The integrity of business answers:** permission metadata and retrieved knowledge that determine what the assistant presents as credible evidence.

## 2. How Would They Most Plausibly Get It?

**Path A — Unauthorized retrieval:** Source permissions are lost, stale, or incorrectly applied during ingestion; a user submits a matching query; restricted content enters prompt assembly and can be reflected in the response. Hiding it after generation would be too late.

**Path B — Poisoned retrieved content:** An attacker influences a document or index entry; the assistant retrieves it; embedded instructions or false source material redirect the response or an allowed downstream action. Treating retrieved text as trusted instructions creates the failure.

## 3. What Have We Already Done About It?

- **Path A — Partial (design and test intent):** The reference specifies trusted identity context, document-level ACL preservation, and pre-generation authorization, with policy/test examples. End-to-end behavior in a live enterprise retrieval system remains **unverified**. [Controls](security-controls.md) · [Tests](../tests)
- **Path B — Partial (defensive design, not proof):** The threat model documents poisoned-content and indirect-injection tests; source controls, separated permissions, and prompt/document defenses are specified. No real-world attack resistance or production incident evidence is claimed. [Technical threat model](threat-model.md) · [Validation checklist](validation-checklist.md)

## 4. What's Left, and What Would Closing It Cost?

1. **Priority 1 — Prove authorization end to end.** Test allowed/denied document retrieval with two users, permission changes, cached/context isolation, and log redaction. **Cost/effort:** synthetic-data setup, engineering/security review and metered search/model usage; estimate pending.
2. **Priority 1 — Test malicious documents and ingestion integrity.** Inject adversarial documents in an isolated corpus and verify source approval, instruction boundaries and safe outputs. **Cost/effort:** curated test cases, evaluator time and safety tooling; estimate pending.
3. **Priority 2 — Establish operations.** Measure per-successful-answer TCO, quality/citations, abuse quotas and alert coverage; assign long-term risk owners. **Cost/effort:** platform/SOC/data-owner time and telemetry; estimate pending.

**Leadership decision:** Authorize a bounded pilot only after data handling, test scope, and cost ceilings are agreed; withhold deployment approval until negative tests pass.  
**Technical basis:** [Threat paths](threat-model.md) · [Controls](security-controls.md) · [Release gates](validation-checklist.md).
