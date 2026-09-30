# Examples

These examples make the architecture concrete without pretending there is one universal RAG implementation.

The samples use the **Azure AI Search security-filter pattern** because it is broadly applicable across data sources and API versions. Azure AI Search also has native document-level ACL/RBAC enforcement options for supported sources; some native capabilities remain preview features, so evaluate them separately for production use.

## What is here

- [document-schema.json](document-schema.json) — sample Azure AI Search index fields for ACL-aware retrieval.
- [sample-documents.json](sample-documents.json) — small document set with different group permissions.
- [authorization-filter.py](authorization-filter.py) — builds a security filter only from trusted group identifiers.
- [adversarial-tests.md](adversarial-tests.md) — practical negative tests for authorization, prompt injection, poisoning, and cross-user leakage.

## Security Filter Pattern

The key field is a filterable collection of group identifiers:

```json
{
  "name": "group_ids",
  "type": "Collection(Edm.String)",
  "filterable": true,
  "retrievable": false
}
```

At query time, the application derives the caller's authorized groups from a **trusted identity source** and applies a filter before retrieval:

```text
group_ids/any(g:search.in(g, '<trusted group IDs>'))
```

Do not accept group IDs or the complete filter expression from the user, the model, or retrieved content.

## Important

Setting an ACL field to `retrievable: false` only keeps that field out of normal search results. It does **not** provide document authorization by itself.

The query must enforce the authorization filter on every retrieval path.

## Native ACL Enforcement

Azure AI Search also supports native document-level access-control approaches for supported Azure Storage / ADLS Gen2 and other integrations. Those approaches compare the caller's Microsoft Entra security principal against permission metadata stored with documents.

Use native authorization when it fits the source and maturity requirements. Use a custom security-filter pattern when you need a custom or cross-platform access model.

## Suggested lab

1. Create three Entra groups or use test GUIDs.
2. Index the sample documents.
3. Map two test users to different groups.
4. Search using User A's trusted group IDs.
5. Verify User A never sees User B's documents.
6. Repeat with semantic/vector queries.
7. Attempt to pass forged group IDs from request parameters.
8. Confirm the application ignores them and builds authorization only from trusted identity context.
