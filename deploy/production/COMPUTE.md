# Deploy the Secure RAG API on Azure Container Apps

This is the final compute layer for the production reference path.

The production platform template now provisions:

- an **internal Azure Container Apps workload-profiles environment** integrated with the production VNet;
- a dedicated `/24` Container Apps infrastructure subnet;
- **Azure Container Registry Premium** with public access disabled;
- an ACR Private Endpoint and `privatelink.azurecr.io` DNS;
- `AcrPull` assigned to the application managed identity.

The application template then deploys the FastAPI image into that internal environment.

## Why this is split into two stages

Infrastructure and application releases have different lifecycles.

**Stage 1 — platform**

```text
VNet
Private DNS
Private Endpoints
Search
Foundry
Key Vault
Log Analytics
ACR
Container Apps Environment
Managed Identities
RBAC
```

**Stage 2 — application**

```text
Build container
Push image
Deploy/update Container App revision
```

This prevents every application release from redeploying core network/security infrastructure.

## 1. Deploy the production platform

```bash
az deployment group create \
  --name secure-rag-prod \
  --resource-group rg-secure-rag-prod \
  --template-file deploy/production/main.bicep \
  --parameters deploy/production/main.parameters.json
```

Capture the outputs:

```bash
ENV_ID=$(az deployment group show -g rg-secure-rag-prod -n secure-rag-prod \
  --query properties.outputs.containerAppsEnvironmentId.value -o tsv)

APP_IDENTITY_ID=$(az deployment group show -g rg-secure-rag-prod -n secure-rag-prod \
  --query properties.outputs.appIdentityResourceId.value -o tsv)

APP_CLIENT_ID=$(az deployment group show -g rg-secure-rag-prod -n secure-rag-prod \
  --query properties.outputs.appIdentityClientId.value -o tsv)

ACR_NAME=$(az deployment group show -g rg-secure-rag-prod -n secure-rag-prod \
  --query properties.outputs.registryName.value -o tsv)

ACR_SERVER=$(az deployment group show -g rg-secure-rag-prod -n secure-rag-prod \
  --query properties.outputs.registryServer.value -o tsv)

SEARCH_ENDPOINT=$(az deployment group show -g rg-secure-rag-prod -n secure-rag-prod \
  --query properties.outputs.searchEndpoint.value -o tsv)

FOUNDRY_ENDPOINT=$(az deployment group show -g rg-secure-rag-prod -n secure-rag-prod \
  --query properties.outputs.foundryEndpoint.value -o tsv)
```

## 2. Build the API image

The production ACR is private by default.

Build and push from a host or runner with network/DNS access to the registry Private Endpoint.

```bash
az acr login --name "$ACR_NAME"

docker build \
  -f app/Dockerfile \
  -t "$ACR_SERVER/secure-rag-api:v1" \
  .

docker push "$ACR_SERVER/secure-rag-api:v1"
```

For CI/CD, use a **self-hosted GitHub Actions runner** or another controlled build agent with private network access rather than opening the production registry to the internet just to make builds easier.

## 3. Deploy the Container App

Use the outputs directly:

```bash
az deployment group create \
  --name secure-rag-api-v1 \
  --resource-group rg-secure-rag-prod \
  --template-file deploy/production/app.bicep \
  --parameters \
    managedEnvironmentId="$ENV_ID" \
    appIdentityResourceId="$APP_IDENTITY_ID" \
    appIdentityClientId="$APP_CLIENT_ID" \
    registryServer="$ACR_SERVER" \
    appImage="$ACR_SERVER/secure-rag-api:v1" \
    searchEndpoint="$SEARCH_ENDPOINT" \
    openaiEndpoint="$FOUNDRY_ENDPOINT" \
    openaiDeployment="<model-deployment-name>"
```

The Container App:

- uses the production application managed identity;
- pulls from private ACR using managed identity;
- reaches Search/Foundry/Key Vault over the VNet and Private DNS;
- has no API keys in its configuration;
- starts with one replica and can scale to three;
- exposes HTTPS ingress on the **internal Container Apps environment**;
- runs liveness/readiness checks against `/healthz`.

## 4. Configure Microsoft Entra authentication

The reference API defaults to:

```text
IDENTITY_MODE=easy_auth
```

That means a trusted authentication layer must inject the validated client principal before traffic reaches the app.

Azure Container Apps supports built-in authentication/authorization. Configure a Microsoft Entra application registration for the API and enable the Container Apps authentication feature so unauthenticated requests are rejected.

The application registration is intentionally **not auto-created in Bicep**. App registrations are tenant identity objects with their own ownership, consent, credential, and lifecycle policies.

After authentication is configured, verify that the app receives a trusted `X-MS-CLIENT-PRINCIPAL` header containing the expected group claims.

### Critical boundary

Do not expose another network path that bypasses the trusted authentication layer while the application trusts `X-MS-CLIENT-PRINCIPAL`.

## 5. Internal DNS and access

The Container Apps environment is internal.

Clients need network reachability to the VNet through an approved path such as:

- peered VNet;
- VPN;
- ExpressRoute;
- Application Gateway or another approved internal ingress tier.

For production deployments, configure DNS for the internal Container Apps environment domain according to your enterprise DNS design.

## 6. Test the complete path

Validate in this order:

1. unauthenticated caller is rejected;
2. authenticated Finance user can reach the API;
3. Finance user can retrieve Finance + shared documents;
4. Finance user cannot retrieve Engineering-only content;
5. Engineering user cannot retrieve Finance-only content;
6. forged group IDs in prompts/headers do not alter authorization;
7. Search resolves through the private endpoint;
8. Foundry resolves through the private endpoint;
9. ACR image pulls succeed through private connectivity;
10. Search/model calls use the application managed identity;
11. diagnostic logs arrive in Log Analytics.

The release gate remains:

> **Unauthorized source text must never reach prompt assembly.**

## Cost note

The production path is intentionally not the cheapest configuration.

Premium ACR, Private Endpoints, Log Analytics, Search replicas, and Container Apps can all incur charges. Use the lab path for inexpensive experimentation and the production path to demonstrate the security architecture.
