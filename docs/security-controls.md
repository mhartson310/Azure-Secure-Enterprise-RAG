# Security Controls

This document maps the architecture's security objectives to practical Azure controls.

## Control Objectives

The architecture is designed around six objectives:

1. **Authenticate every requester and workload.**
2. **Authorize retrieval before generation.**
3. **Preserve data permissions during ingestion.**
4. **Treat retrieved content as untrusted input.**
5. **Minimize network and credential exposure.**
6. **Make the complete RAG path observable and testable.**

## Control Matrix

| Security objective | Azure capability | Implementation guidance | Validation evidence |
|---|---|---|---|
| Human authentication | Microsoft Entra ID | Use modern authentication, MFA/Conditional Access as appropriate, and group/role claims required by the application. | Sign-in logs, CA results, token claims. |
| Workload authentication | Managed Identity | Prefer managed identity for Azure-to-Azure authentication instead of embedded keys. | Role assignments, token-based access, absence of stored secrets. |
| Retrieval authorization | Azure AI Search document-level access control / security filters | Preserve ACL or principal metadata and enforce user/group authorization at query time. | Negative tests showing restricted documents are excluded. |
| Search access | Azure RBAC | Grant only required data-plane roles to application identities. Separate query from index-management permissions. | RBAC export and least-privilege review. |
| Secret protection | Azure Key Vault | Store remaining secrets, certificates, and keys centrally. Rotate and audit access. | Vault access logs, rotation evidence. |
| Network isolation | Private Link / private endpoints | Disable or minimize public network paths where supported and operationally appropriate. | Network configuration, private DNS resolution, connectivity tests. |
| Prompt attack detection | Azure AI Content Safety Prompt Shields | Analyze direct user prompts and retrieved documents for adversarial instructions. | Prompt-injection test results and alert/log evidence. |
| Data governance | Microsoft Purview | Classify sensitive sources and align data handling with organizational policy. | Classification labels, policies, data-map evidence. |
| Platform guardrails | Azure Policy | Enforce required configuration such as private endpoints, approved regions, diagnostics, and identity controls. | Policy assignments and compliance state. |
| Security posture | Microsoft Defender for Cloud / relevant Defender capabilities | Monitor workload posture and cloud security findings for supporting infrastructure. | Recommendations, alerts, secure score evidence as applicable. |
| Telemetry | Azure Monitor / Log Analytics | Capture authentication, application, search, networking, and model/API telemetry. | Centralized logs, dashboards, alerts. |
| Abuse prevention | API gateway / service quotas / rate limits | Apply rate limiting, quotas, request validation, and anomaly detection. | Throttling tests, quota configuration, alerts. |
| Response traceability | Application logging + citations | Record source identifiers, request correlation, retrieval decisions, and response metadata without logging unnecessary sensitive content. | Correlated traces and reproducible source references. |

## Retrieval Authorization Patterns

Azure AI Search supports multiple authorization approaches. Choose deliberately based on data source and service capability.

### Native document-level access control

Where supported, preserve source permission metadata and enforce access using the caller's Microsoft Entra identity during query processing.

### Security-filter pattern

For custom access models, store user/group identifiers with indexed documents and apply a filter based on trusted identity context from the application.

**Important:** a string-based security filter is only as trustworthy as the identity context used to build it. Never accept group IDs, tenant IDs, or authorization filters directly from untrusted user input.

## Identity Design Rules

- Human identity and workload identity are different security boundaries.
- Prefer managed identity for service-to-service authentication.
- Separate runtime query permissions from index administration.
- Use least privilege for ingestion pipelines.
- Avoid shared application secrets when an identity-based option is available.
- Do not let the model construct or override authorization filters.

## Data and Ingestion Controls

The ingestion pipeline is part of the security boundary.

Required considerations:

- approved source inventory;
- source ownership and provenance;
- preservation of ACLs and sensitivity metadata;
- restricted write access;
- schema and enrichment change control;
- malware/content scanning where relevant;
- index update logging;
- handling for deleted or access-revoked source documents;
- review of stale or orphaned permissions.

## Prompt and Context Controls

Retrieved text should be handled as **data**, not instructions.

Recommended layers:

- system/developer instructions that explicitly separate trusted instructions from retrieved content;
- Prompt Shields for user and document attacks;
- clear delimiters or spotlighting for external content;
- bounded context windows;
- allowlisted tools and actions;
- deterministic checks before high-impact actions;
- output validation and safe rendering.

No single prompt-injection control is sufficient by itself.

## Network Controls

Consider:

- private endpoints for Azure AI Search, model endpoints, Key Vault, and supporting services where supported;
- restricted egress from application workloads;
- private DNS validation;
- explicit firewall rules;
- disabling public network access when operationally viable;
- separate subnets for application, data, and management components where justified.

## Monitoring

At minimum, correlate:

- user identity and session;
- application request ID;
- retrieval query and filter decision;
- search/index response metadata;
- model deployment and request;
- policy or guardrail result;
- response status;
- security alerts and throttling events.

Avoid indiscriminately logging full prompts or retrieved sensitive content.

## Priority Controls

If implementing this architecture incrementally, start here:

1. Entra ID authentication.
2. Retrieval-time authorization.
3. ACL-preserving ingestion.
4. Managed identity and least privilege.
5. Prompt/document attack controls.
6. Central telemetry.
7. Private connectivity where appropriate.
8. Negative authorization and prompt-injection testing.
