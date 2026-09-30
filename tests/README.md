# Automated Security Tests

This test harness turns several of the repository's security claims into executable checks.

## What is tested

### Authorization filter construction

`test_authorization_filter.py` verifies that:

- trusted group GUIDs produce a valid Azure AI Search security filter;
- duplicate group IDs are de-duplicated;
- missing identity context fails closed;
- malformed or injected group values are rejected before query construction.

### Retrieval-policy behavior

`test_retrieval_policy.py` uses the sample ACL-aware documents to verify that:

- Finance users only see Finance + shared content;
- Engineering users only see Engineering + shared content;
- users with no approved groups see nothing;
- exact-title requests cannot bypass authorization;
- semantic relevance cannot reintroduce a document removed by the authorization boundary;
- result sets remain isolated across identities.

## Run locally

```bash
python -m pip install -r requirements-dev.txt
pytest -q
```

## Security property being proven

The core assertion is:

> **Authorization reduces the candidate document set before ranking, prompt assembly, or model inference.**

These tests intentionally focus on the authorization boundary. They do not claim to emulate Azure AI Search's ranking engine or Microsoft Entra ID.
