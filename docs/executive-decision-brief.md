# Executive Decision Brief — Secure Enterprise RAG on Azure

**Decision requested:** Approve a limited, security-gated evaluation of permission-aware enterprise retrieval and grounded answers.  
**Audience:** AI/platform leadership, data owners, security sponsor, and budget owner  
**Status:** PROPOSED — not approval for production AI use or a vendor endorsement

## 1. The Ask

Approve a non-production comparison of existing enterprise search against the proposed retrieval-and-generation pattern, using synthetic or specifically approved content and at least two differently authorized test users. Name the sponsor and approve the time box and budget **before** consuming paid services.

## 2. Why Now

The [architecture](../architecture/README.md), [threat model](threat-model.md), authorization patterns, and test checklist exist, but the repository has no demonstrated live enterprise rollout. The next decision is whether generation offers measurable task value **without permitting restricted documents into model context**. A simpler search solution remains a valid outcome.

## 3. What It Costs

**Budget: not yet estimated.** Cost drivers include source preparation, ACL synchronization, indexing/storage, retrieval, input/output tokens, safety evaluation, networking, monitoring, and ongoing model/content operations. Include security and data-owner review time and the delivery work displaced by the pilot; use dated prices and a workload-based TCO model, not generic model rankings.

## 4. Cost of Inaction

Without measured authorization, answer quality, and per-task costs, leadership cannot distinguish a valuable enterprise assistant from a costly or unsafe search substitute. Proceeding to deployment without the evaluation could leave data-access and misinformation risks unresolved. **Neither financial impact nor likelihood has been measured.**

## 5. What Happens Next

The business owner identifies representative tasks and a measurable non-AI baseline; data/security owners define authorization test identities, negative tests, and approval gates. The pilot compares task outcomes and costs, verifies retrieval controls **before generation**, then returns an approve/revise/reject recommendation with sanitized evidence.

**Release blocker:** An unauthorized document reaching prompt assembly is unacceptable.  
**Supporting detail:** [Architecture decision guide](decision-framework/README.md) · [Security controls](security-controls.md) · [Validation checklist](validation-checklist.md) · [Leadership threat summary](threat-model-leadership-summary.md).
