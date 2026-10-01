# Secure RAG API

This lightweight FastAPI application turns the repository architecture into a runnable reference implementation.

The request path is:

```text
Caller
  ↓
Trusted identity boundary
  ↓
FastAPI application
  ↓
Derive trusted group IDs
  ↓
Azure AI Search with authorization filter
  ↓
Authorized chunks only
  ↓
Azure OpenAI / Foundry model
  ↓
Answer + citations
```

## Security properties

The application is deliberately designed around these rules:

1. **The model never decides authorization.**
2. **The client never supplies its own authorization filter.**
3. **Group IDs are derived from trusted identity context.**
4. **Search is filtered before prompt assembly.**
5. **Only authorized search results are sent to the model.**
6. **Citations are generated from retrieved source metadata, not invented by the model.**
7. **The API fails closed when identity context is missing or invalid.**

## Identity modes

### Azure App Service / Easy Auth

Set:

```text
IDENTITY_MODE=easy_auth
```

The app reads the trusted `X-MS-CLIENT-PRINCIPAL` header that Azure App Service Authentication injects after validating the caller.

Do **not** expose the application directly in a way that lets clients bypass the trusted authentication boundary and forge this header.

### Local development

Set:

```text
IDENTITY_MODE=debug
ALLOW_DEBUG_IDENTITY=true
```

Then supply a local-only header:

```text
X-Debug-Group-Ids: 11111111-1111-1111-1111-111111111111
```

Debug identity is intentionally disabled unless explicitly enabled.

Never use debug mode in production.

## Required environment variables

See [`.env.example`](.env.example).

At minimum:

```text
AZURE_SEARCH_ENDPOINT=https://<search-service>.search.windows.net
AZURE_SEARCH_INDEX=enterprise-rag-demo
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=<deployment-name>
IDENTITY_MODE=easy_auth
```

The app uses `DefaultAzureCredential` for Azure AI Search and Azure OpenAI.

## Run locally

```bash
python -m pip install -r app/requirements.txt
uvicorn app.main:app --reload --port 8000
```

Health check:

```bash
curl http://localhost:8000/healthz
```

Debug-mode example:

```bash
export IDENTITY_MODE=debug
export ALLOW_DEBUG_IDENTITY=true

curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -H "X-Debug-Group-Ids: 11111111-1111-1111-1111-111111111111" \
  -d '{"question":"What are the FY27 finance planning assumptions?"}'
```

## Production deployment

Recommended production posture:

- App Service / Container Apps / AKS with Microsoft Entra authentication;
- private connectivity to Search, Foundry/Azure OpenAI, and Key Vault;
- user-assigned managed identity for the application;
- `Search Index Data Reader` on the Search service;
- `Cognitive Services OpenAI User` on the AI resource;
- no Search API keys;
- `IDENTITY_MODE=easy_auth`;
- no debug identity;
- centralized logging with prompts/content minimized or redacted.

## Group overage

Microsoft Entra tokens may omit full group membership when a user belongs to many groups and instead emit an overage indicator.

This sample intentionally **fails closed** if trusted group claims are unavailable.

A production application that needs to support group overage should resolve membership through an approved server-side path such as Microsoft Graph, cache it carefully, and preserve tenant/user isolation.

## Endpoints

### `GET /healthz`

Returns service health without touching Search or the model.

### `POST /query`

Request:

```json
{
  "question": "What are the platform architecture standards?"
}
```

Response:

```json
{
  "answer": "...",
  "citations": [
    {
      "document_id": "engineering-001",
      "title": "Platform Architecture Standards",
      "source_uri": "https://contoso.example/engineering/architecture"
    }
  ]
}
```

## What this sample intentionally does not do

- client-controlled authorization filters;
- model-generated authorization logic;
- tool/agent execution;
- conversation memory;
- broad prompt/content logging;
- automatic Graph group expansion;
- production-grade rate limiting.

Those should be added deliberately, not hidden inside a demo.


## Security telemetry

The application emits structured, single-line JSON security events through [`telemetry.py`](telemetry.py).

Current events include:

- `rag_query_started`
- `rag_query_completed`
- `rag_no_authorized_context`
- `rag_authorization_denied`
- `rag_request_failed`

The telemetry intentionally avoids raw prompts, retrieved content, generated responses, tokens, and secrets. User and tenant identifiers are pseudonymized before logging.

See the [Microsoft Sentinel + KQL integration](../sentinel/README.md) for hunting queries, detection candidates, and triage guidance.
