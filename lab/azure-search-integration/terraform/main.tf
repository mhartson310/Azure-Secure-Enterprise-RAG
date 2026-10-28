resource "azurerm_resource_group" "lab" {
  name     = var.resource_group_name
  location = var.location
  tags     = local.tags
}

locals {
  tags = merge(var.tags, {
    workload   = "secure-rag-retrieval-validation"
    lifecycle  = "disposable-lab"
    managed-by = "terraform"
  })
}

# Deliberately public/key-authenticated for a low-cost Free-tier integration lab.
# NOT a production Zero Trust deployment; see README.md for the control gaps.
resource "azurerm_search_service" "lab" {
  name                = var.search_service_name
  resource_group_name = azurerm_resource_group.lab.name
  location            = azurerm_resource_group.lab.location
  sku                 = "free"
  replica_count       = 1
  partition_count     = 1

  public_network_access_enabled = true
  local_authentication_enabled  = true

  tags = local.tags
}
