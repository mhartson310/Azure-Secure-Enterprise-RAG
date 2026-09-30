# Threat Model

This threat model focuses on the security boundary between user identity, retrieval, enterprise data, prompt assembly, and model inference.

> **Key principle:** retrieved content is untrusted input, and authorization must be enforced before source text reaches the model.

## Assets

| Asset | Why it matters |
|---|---|
| User identity and claims | Drives authorization decisions and determines what content can be retrieved. |
| Enterprise source data | May contain confidential, regulated, or business-sensitive information. |
| Search index and embeddings | Can expose source content, permissions, or semantic relationships if misused. |
| ACL / permission metadata | Determines document-level access during retrieval. |
| System prompts | Define application behavior and security boundaries. |
| Retrieved context | Can contain malicious instructions, poisoned content, or sensitive data. |
| Model endpoint | Can be abused for cost, exfiltration, or policy bypass. |
| Application/API layer | Orchestrates identity, retrieval, prompt construction, policy, and output handling. |
| Telemetry and audit logs | Required for detection, investigation, and control validation. |

## Trust Boundaries

1. **User → Entra ID** — authenticate the human or calling principal.
2. **Entra ID → Application/API** — establish trusted identity and authorization context.
3. **Application/API → Azure AI Search** — retrieve only content authorized for that identity.
4. **Enterprise Sources → Ingestion Pipeline** — validate source integrity and preserve permissions.
5. **Search → Prompt Assembly** — treat retrieved text as untrusted content.
6. **Application/API → Model** — restrict model access and bound the context sent for inference.
7. **Model → User** — validate, filter, cite, and log responses before display.

## Threat Scenarios

| Threat | Attack path | Impact | Primary mitigations |
|---|---|---|---|
| Direct prompt injection | User attempts to override system behavior or security instructions. | Policy bypass, unsafe output, unintended actions. | Prompt Shields, strict system instructions, input validation, least-privilege tool access, output checks. |
| Indirect prompt injection | Malicious instructions are embedded in retrieved documents. | Model follows attacker-controlled instructions from trusted-looking content. | Treat retrieved data as untrusted, Prompt Shields for documents, isolation/spotlighting, source controls, bounded tools. |
| RAG poisoning | Attacker inserts or alters content that is later indexed. | Manipulated answers, persistent misinformation, credential harvesting, malicious instructions. | Source provenance, restricted ingestion writes, content validation, approval workflows, integrity monitoring. |
| Unauthorized retrieval | Search returns content outside the caller's permissions. | Sensitive-data disclosure before generation. | Document-level authorization, ACL preservation, trusted user context, negative authorization tests. |
| Sensitive data leakage | Authorized or unauthorized context is exposed in responses or logs. | Privacy, compliance, contractual, or business impact. | Data classification, minimization, DLP, output filtering, telemetry hygiene, retention controls. |
| Model/API abuse | Endpoint is used for high-volume abuse, jailbreaks, or resource exhaustion. | Cost impact, service degradation, abuse of AI capability. | Entra ID, managed identity, quotas, rate limits, network restrictions, anomaly detection. |
| System prompt extraction | Attacker attempts to recover hidden application instructions. | Disclosure of controls and internal logic. | Avoid secrets in prompts, layered controls, output filtering, separate secrets from instructions. |
| Retrieval credential harvesting | Poisoned content attempts to trick users/agents into exposing secrets. | Credential theft or lateral movement. | No secrets in model context, safe rendering, link controls, user education, agent/tool least privilege. |
| Index tampering | Unauthorized actor changes index schema, documents, ACLs, or enrichment logic. | Broad integrity or confidentiality failure. | RBAC separation, managed identity, restricted admin roles, change logging, CI/CD controls. |
| Cross-user context leakage | Cache, session, memory, or prompt construction leaks one user's data to another. | Data exposure across tenants/users. | Session isolation, cache partitioning, stateless authorization checks, tenant-aware keys and filters. |

## MITRE ATLAS Candidate Mappings

MITRE ATLAS is a living knowledge base, so these mappings are best treated as **threat-model references rather than rigid one-to-one classifications**.

| RAG threat | Relevant ATLAS techniques |
|---|---|
| Direct prompt injection | **LLM Prompt Injection**, **LLM Jailbreak**, **LLM Prompt Crafting** |
| Indirect prompt injection | **Retrieval Content Crafting**, **LLM Prompt Injection**, **Prompt Infiltration via Public-Facing Application** |
| RAG poisoning | **RAG Poisoning**, **False RAG Entry Injection**, **Retrieval Content Crafting** |
| Sensitive data leakage | **LLM Data Leakage**, **Data from AI Services**, **Exfiltration via AI Inference API** |
| Credential harvesting through RAG | **RAG Credential Harvesting**, **Credentials from AI Agent Configuration** where agentic components are present |
| API/model abuse | **Cost Harvesting**, **Denial of AI Service**, **Evade AI Model** |
| Prompt/system discovery | **Extract LLM System Prompt**, **Discover LLM System Information** |
| Manipulated retrieved context | **AI Agent Context Poisoning** for agentic variants, plus **RAG Poisoning** |

## Abuse Cases to Test

### Test 1 — Direct prompt override
Ask the assistant to ignore system instructions and disclose restricted internal content.

**Expected:** the request is rejected or safely constrained; no restricted context is retrieved.

### Test 2 — Indirect injection in a document
Insert malicious instructions into an otherwise legitimate document and force it into the retrieval set.

**Expected:** the document is treated as untrusted data; embedded instructions do not alter application policy.

### Test 3 — Unauthorized semantic match
Use a user who lacks access to a document, then submit a query semantically similar to that restricted content.

**Expected:** the restricted document is never returned by retrieval.

### Test 4 — Poisoned knowledge source
Attempt to add malicious or false content through an ingestion path.

**Expected:** unauthorized writes are blocked and approved-source provenance is preserved.

### Test 5 — Cross-user leakage
Run similar queries from two users with different permissions.

**Expected:** each receives only the content their identity permits.

### Test 6 — High-volume endpoint abuse
Generate repeated model and retrieval calls above expected workload patterns.

**Expected:** quotas, throttling, and monitoring respond as designed.

## Review Questions

- Can any application path bypass the retrieval authorization filter?
- Can indexed content lose or inherit the wrong ACL during ingestion?
- Can a malicious document influence system instructions or tool execution?
- Can restricted data appear in logs, traces, caches, or evaluation datasets?
- Can a compromised workload identity modify both the index and query it?
- Are index administration and runtime query permissions separated?
- Can user-controlled metadata alter authorization filters?
- Are negative tests part of release validation?

## References

- MITRE ATLAS: https://atlas.mitre.org/
- Microsoft guidance on document-level access control in Azure AI Search
- Microsoft Prompt Shields guidance for user and document attacks
