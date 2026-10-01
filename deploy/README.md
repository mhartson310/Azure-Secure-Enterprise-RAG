# Azure Deployment Path

This folder provides a deliberately small deployment path for the **Secure Enterprise RAG on Azure** reference architecture.

The goal is to make the architecture testable without pretending a low-cost lab is production-ready.

## What the Bicep template deploys

- **Azure AI Search**
  - System-assigned managed identity
  - Microsoft Entra + API-key authentication during the lab
  - One replica / one partition
  - Semantic ranker setting exposed as a parameter
- **Microsoft Foundry / Azure AI Services**
  - System-assigned managed identity
  - No model deployment by default
- Resource outputs for the Search and Foundry endpoints

It intentionally does **not** deploy:

- a model deployment;
- an application/API compute tier;
- Private Endpoints or VNets;
- Key Vault;
- production monitoring/alerting;
- enterprise data connectors.

Those are separate security and cost decisions rather than hidden defaults.

## Cost-conscious profiles

### Profile A — Learning / validation

Use:

```text
searchSku = free
publicNetworkAccess = Enabled
disableSearchLocalAuth = false
```

This is the lowest-friction path. Azure AI Search allows one Free service per subscription and Free has limited capacity/features.

Use this profile to validate:

- the index schema;
- ACL-aware filtering;
- sample documents;
- negative authorization tests.

### Profile B — Security-feature lab

Use:

```text
searchSku = basic
publicNetworkAccess = Enabled
disableSearchLocalAuth = false
```

Basic is the better starting point when you need capabilities that aren't supported on the Free tier. Azure AI Search documents feature differences by SKU; for example, inbound Private Link isn't available on Free.

### Profile C — Production hardening

Start with Basic/Standard as workload requirements dictate, then add:

- Private Endpoints and private DNS;
- API-key disablement after RBAC is proven;
- workload identities and least-privilege role assignments;
- Key Vault where secrets remain necessary;
- centralized logging and alerting;
- Purview / Policy controls;
- source-specific ACL synchronization;
- production model deployment and Responsible AI policy;
- resilience/capacity appropriate to the workload.

Do not treat the lab template as a production landing zone.

## Prerequisites

- Azure subscription
- Azure CLI
- Bicep CLI (Azure CLI can install/manage it)
- Permissions to create Search and Cognitive Services resources

Check tooling:

```bash
az version
az bicep version
```

If needed:

```bash
az bicep install
```

## Deploy

### 1. Sign in

```bash
az login
az account set --subscription "<subscription-id-or-name>"
```

### 2. Create a resource group

Choose a region that supports the services/models you intend to use.

```bash
az group create \
  --name rg-secure-rag-lab \
  --location westus2
```

### 3. Validate the template

```bash
az deployment group validate \
  --resource-group rg-secure-rag-lab \
  --template-file deploy/main.bicep \
  --parameters deploy/main.parameters.json
```

### 4. Preview changes

```bash
az deployment group what-if \
  --resource-group rg-secure-rag-lab \
  --template-file deploy/main.bicep \
  --parameters deploy/main.parameters.json
```

### 5. Deploy

```bash
az deployment group create \
  --name secure-rag-lab \
  --resource-group rg-secure-rag-lab \
  --template-file deploy/main.bicep \
  --parameters deploy/main.parameters.json
```

Capture the Search endpoint:

```bash
SEARCH_ENDPOINT=$(az deployment group show \
  --resource-group rg-secure-rag-lab \
  --name secure-rag-lab \
  --query properties.outputs.searchEndpoint.value \
  --output tsv)

echo "$SEARCH_ENDPOINT"
```

## Bootstrap the ACL-aware index

The repository includes a small Python bootstrap script using `DefaultAzureCredential`.

Install dependencies:

```bash
python -m pip install -r deploy/requirements.txt
```

Set the endpoint:

```bash
export AZURE_SEARCH_ENDPOINT="$SEARCH_ENDPOINT"
```

Then run:

```bash
python deploy/scripts/bootstrap_index.py
```

The script creates the demo index and uploads the ACL-aware sample documents from `examples/sample-documents.json`.

### Required Search data-plane permissions

Your signed-in identity needs permission to create/write the index and documents.

For a real deployment, assign the minimum required Azure AI Search data-plane role(s) to the operator/workload identity rather than falling back to admin keys.

## Test

Run the local security tests:

```bash
python -m pip install -r requirements-dev.txt
pytest -q
```

Then use the sample group IDs to test retrieval:

- Finance: `11111111-1111-1111-1111-111111111111`
- Engineering: `22222222-2222-2222-2222-222222222222`

The test objective is not "the chatbot answered correctly." It is:

> **Can an unauthorized document enter the candidate set or prompt context?**

## Model deployment

The Bicep template creates a Foundry/Azure AI Services resource but deliberately does not choose or deploy a model.

Model availability, versions, quotas, deployment types, and regional support change independently from the architecture. Deploy a model after confirming the appropriate region, model, capacity, and pricing for your subscription.

This keeps the infrastructure sample reproducible and avoids silently creating a billable model deployment.

## Tear down

The safest way to avoid leaving a lab running is to delete the resource group when you're finished:

```bash
az group delete \
  --name rg-secure-rag-lab \
  --yes \
  --no-wait
```

## Production-hardening path

A separate production-oriented baseline is now available at [`deploy/production/`](production/README.md).

It adds Private Endpoints, Private DNS, RBAC-only Search access, Key Vault, Log Analytics diagnostics, and explicit separation between the runtime application identity and the ingestion identity while keeping the low-cost lab intentionally simple.
