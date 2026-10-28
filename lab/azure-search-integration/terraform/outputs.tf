output "search_endpoint" {
  description = "Public Free-tier Search endpoint for this disposable lab."
  value       = "https://${azurerm_search_service.lab.name}.search.windows.net"
}

output "search_service_name" {
  value = azurerm_search_service.lab.name
}

output "resource_group_name" {
  value = azurerm_resource_group.lab.name
}

output "security_scope" {
  value = "FREE-TIER LAB ONLY: public endpoint and key auth; no private networking, managed identity or production security claim."
}
