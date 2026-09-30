# Validation Checklist

Use this checklist before promoting an enterprise RAG workload into production and whenever identity, source systems, indexing, retrieval, or model configuration changes.

## 1. Identity

- [ ] All human users authenticate through the approved identity provider.
- [ ] MFA and Conditional Access requirements are defined where appropriate.
- [ ] Application/service components use managed identity where supported.
- [ ] No production credentials are hard-coded in source code or prompts.
- [ ] Workload identities have only the roles they require.
- [ ] Runtime query identities cannot administer the index unless explicitly required.

## 2. Authorization

- [ ] Retrieval authorization is enforced **before prompt assembly**.
- [ ] Authorization context comes from trusted identity claims, not user-supplied parameters.
- [ ] Document-level ACLs or security metadata are preserved during ingestion.
- [ ] Group membership behavior is understood and tested.
- [ ] Tenant boundaries are explicit.
- [ ] Revoked access is reflected in the index within an acceptable time window.
- [ ] A user cannot bypass filters by changing query syntax, metadata, or semantic similarity.

## 3. Negative Authorization Tests

Create at least two test identities with intentionally different access.

- [ ] User A can retrieve Document A.
- [ ] User A cannot retrieve Document B.
- [ ] User B can retrieve Document B.
- [ ] User B cannot retrieve Document A.
- [ ] Semantic queries do not expose unauthorized documents.
- [ ] Exact-title queries do not expose unauthorized documents.
- [ ] Metadata filters cannot be manipulated to broaden access.
- [ ] Restricted content is absent from model context, not merely hidden in the final answer.

## 4. Ingestion Integrity

- [ ] Only approved data sources can feed the index.
- [ ] Ingestion writers are tightly restricted.
- [ ] Source provenance is retained.
- [ ] ACL and sensitivity metadata are preserved.
- [ ] Deleted source documents are removed from the index.
- [ ] Permission changes are synchronized.
- [ ] Index schema changes are reviewed.
- [ ] Content-enrichment logic is version controlled.
- [ ] Poisoned or malformed documents are handled safely.

## 5. Prompt Injection

Test both direct and indirect attacks.

- [ ] Direct requests to ignore system instructions are handled safely.
- [ ] Role-play jailbreak attempts do not bypass policy.
- [ ] Encoded or obfuscated instructions are tested.
- [ ] Malicious instructions embedded in retrieved documents are tested.
- [ ] Retrieved content cannot redefine the system role.
- [ ] Retrieved content cannot invoke tools outside allowed policy.
- [ ] Prompt Shields or equivalent controls are tested with known attack samples.
- [ ] Fail-open vs fail-closed behavior is explicitly understood.

## 6. RAG Poisoning

- [ ] Unauthorized users cannot add or alter indexed knowledge.
- [ ] Approved sources are allowlisted or otherwise governed.
- [ ] Provenance is available for retrieved content.
- [ ] High-risk source changes can be audited.
- [ ] Known poisoned-content test cases do not silently alter system behavior.
- [ ] Critical knowledge sources have ownership and review processes.

## 7. Sensitive Data

- [ ] Sensitive-data categories are documented.
- [ ] Retrieval minimizes unnecessary sensitive fields.
- [ ] Responses are tested for accidental disclosure.
- [ ] Logs do not store unnecessary secrets or sensitive context.
- [ ] Evaluation datasets are governed.
- [ ] Cache/session design prevents cross-user leakage.
- [ ] Data-retention requirements are defined.

## 8. Model and API Abuse

- [ ] Model endpoints require authenticated access.
- [ ] Rate limits and quotas are configured.
- [ ] High-volume abuse scenarios are tested.
- [ ] Cost anomalies generate alerts.
- [ ] Repeated policy bypass attempts can be detected.
- [ ] Public endpoint exposure is minimized.

## 9. Network Security

- [ ] Private endpoints are configured where required.
- [ ] Private DNS resolution works as intended.
- [ ] Public network access is disabled where appropriate.
- [ ] Egress paths are understood and restricted where needed.
- [ ] Network rules are tested from both allowed and denied locations.

## 10. Observability

- [ ] Authentication events are available.
- [ ] Retrieval requests can be correlated with application requests.
- [ ] Search failures and authorization failures are logged.
- [ ] Model/API usage is monitored.
- [ ] Prompt-attack detections are logged.
- [ ] Index changes are auditable.
- [ ] Security alerts route to an owned response process.
- [ ] Logging avoids creating a secondary sensitive-data repository.

## 11. Response Quality and Grounding

- [ ] Responses cite or reference supporting sources where appropriate.
- [ ] Retrieved passages actually support the response.
- [ ] The model does not invent inaccessible sources.
- [ ] The application handles no-result conditions safely.
- [ ] Grounding/evaluation tests include sensitive and adversarial scenarios.

## 12. Operational Readiness

- [ ] Security owners are identified.
- [ ] Data-source owners are identified.
- [ ] Incident-response procedures include AI/RAG scenarios.
- [ ] Key rotation and credential-recovery procedures are documented.
- [ ] Index rebuild/recovery procedures are tested.
- [ ] Rollback exists for model, prompt, index, and ingestion changes.
- [ ] The threat model is reviewed after material architecture changes.

## Release Gate

A production release should not pass security validation if either condition is true:

1. **An unauthorized document can reach prompt assembly.**
2. **Untrusted retrieved content can change privileged application behavior without another control stopping it.**
