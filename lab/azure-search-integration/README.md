# Azure AI Search Free-tier authorization lab — Terraform

**Status: NOT DEPLOYED / LIVE TESTS NOT RUN.** This is a reproducible, low-cost **synthetic group-ACL retrieval lab**, not proof of production authentication, managed identity, tenant isolation, or end-to-end LLM security.

## Purpose and boundary

Provision one disposable Azure AI Search Free-tier service with Terraform; create the existing sample index and documents; execute positive and negative retrieval checks against real Azure AI Search; record the outcome. The local `policy.py` gate uses a **separate hard-coded synthetic fixture ACL** to simulate independent authorization. It is **not wired into the production FastAPI request path** and must not be presented as proof of an independently authoritative production permission service.

The Free tier has limited features and may not be available for creation if a subscription already has a Free Search service. **Public networking and API-key authentication are enabled intentionally for this isolated lab.** Do not put real documents or identities here. Azure Search API keys authorize access to the Search service and **do not establish an end-user's identity**.

## Prerequisites

- Azure subscription with permission to create a resource group and Search service; Azure CLI logged in with `az login`.
- Terraform >=1.6, AzureRM provider ~>4.0, Python >=3.12.
- A globally unique Search service name; confirm Free-tier quota and regional availability in your subscription.
- Use only the committed synthetic Contoso documents. **No production data.**
- Review any Azure subscription charges and quotas before applying; Terraform itself does not guarantee zero cost.

## Provision

```bash
cd lab/azure-search-integration/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit subscription_id, globally unique search_service_name, location and tags.
terraform init
terraform fmt -check
terraform validate
terraform plan -out=tfplan
# Review plan, especially Free SKU and public/key-auth configuration.
terraform apply tfplan
terraform output -raw search_endpoint
```

Use a local state file only for this temporary lab; never commit state, plan files, tfvars, API keys or environment files. For team use, move to a secured remote backend with access controls and state encryption.

## Create index and load synthetic documents

The existing repository bootstrap script is reused rather than maintaining a second index schema. The following commands assume the repo root as your working directory. Retrieve the key from the Azure portal under the **lab Search service > Keys** and set it as a local environment variable. Do not paste it into a terminal command that is saved to shell history, GitHub issues, or screenshots.

```bash
python -m pip install -r app/requirements.txt -r lab/azure-search-integration/requirements.txt
export AZURE_SEARCH_ENDPOINT="https://YOUR-SERVICE.search.windows.net"
export AZURE_SEARCH_INDEX="enterprise-rag-demo"
read -rs AZURE_SEARCH_ADMIN_KEY
export AZURE_SEARCH_ADMIN_KEY
python deploy/scripts/bootstrap_index.py
```

**Important:** The bootstrap script uses `AZURE_SEARCH_ADMIN_KEY` if set. The existing FastAPI `SecureSearch` class uses `DefaultAzureCredential`, not this key; this Free-tier integration package therefore tests Azure Search retrieval and the synthetic independent result gate, **not a live authenticated FastAPI request**.

## Offline tests (safe in CI)

```bash
cd lab/azure-search-integration
python -m pytest -q test_policy.py
```

## Opt-in live integration tests

After provisioning and indexing, from `lab/azure-search-integration`:

```bash
export LIVE_AZURE_SEARCH_TESTS=1
python -m pytest -q test_live_search.py
unset LIVE_AZURE_SEARCH_TESTS AZURE_SEARCH_ADMIN_KEY
```

These tests use fixture group IDs as trusted inputs. They check expected document sets, fail-closed empty membership, title-based bypass attempts, and rejection of a deliberately injected result. **They do not test real Entra tokens, cross-tenant authorization, revocation propagation, malicious-prompt efficacy, private endpoints, or managed identities.** Those remain explicit future milestones.

## Evidence capture

Keep raw output and subscription/resource identifiers private. Copy the redacted schema at `evidence/example-redacted.json`, populate **actual** UTC timestamps, individual test outcomes and GitHub Actions links only after execution, and manually review it for secrets and tenant/user IDs. Generated `evidence/*.json` is gitignored. Never mark a test PASS based solely on the existence of this code.

## Teardown

```bash
cd lab/azure-search-integration/terraform
terraform destroy
```

Review the destroy plan and verify that the lab resource group and Search service are gone in the Azure portal. The Free-tier allocation and service-name availability may take time to clear. Destroying the resource group removes the index and synthetic data. Do not delete a resource group shared with other workloads.

## Upgrade path

A separate production-grade lab should use a supported paid tier, private endpoints, Entra/RBAC-based Search access, trusted token validation, permission freshness/revocation, tenant-aware ACLs, telemetry and independent authorization on the **actual FastAPI retrieval path**. Those controls are intentionally **not** claimed here.
