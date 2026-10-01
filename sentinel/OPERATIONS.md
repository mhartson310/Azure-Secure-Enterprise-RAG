# Sentinel Operational Notes

## Suggested analytics-rule cadence

| Detection | Frequency | Lookback | Starting threshold |
|---|---:|---:|---:|
| Repeated authorization denials | 5 min | 15 min | 10/user |
| Request failure spike | 5 min | 10 min | 10 total |
| Unusual retrieval volume | 5 min | 15 min | tune from baseline |

These are **starting points**, not universal thresholds.

## Incident triage questions

For a RAG-related Sentinel alert, ask:

1. Is the caller expected?
2. Did the same identity recently experience authorization failures?
3. Did the request retrieve any documents?
4. Which document IDs appeared in the retrieval set?
5. Did Search operations change at the same time?
6. Did the application revision, managed identity, or RBAC configuration change?
7. Did model-call failures or volume change?
8. Is the behavior isolated to one identity/tenant or broad across the service?
9. Is there evidence of an ingestion/index change before the behavior began?
10. Can the activity be reproduced with a known test identity?

## Useful correlation key

Every RAG request gets an `X-Correlation-ID`.

The same value is emitted in application security telemetry. Propagate this identifier into downstream calls where supported so investigations can pivot from:

```text
Sentinel alert
→ application event
→ RAG request
→ retrieval activity
→ model call
```

without logging prompts or document content.
