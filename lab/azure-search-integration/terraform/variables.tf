variable "subscription_id" {
  description = "Azure subscription GUID. Set via TF_VAR_subscription_id or -var."
  type        = string
  validation {
    condition     = can(regex("^[0-9a-fA-F-]{36}$", var.subscription_id))
    error_message = "subscription_id must be a GUID."
  }
}

variable "location" {
  description = "Azure region where Free-tier Azure AI Search is available."
  type        = string
  default     = "westus2"
}

variable "resource_group_name" {
  description = "Dedicated disposable resource group."
  type        = string
  default     = "rg-rag-authz-lab"
}

variable "search_service_name" {
  description = "Globally unique Search service name (2–60 lowercase alphanumeric or hyphen characters)."
  type        = string
  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{0,58}[a-z0-9]$", var.search_service_name))
    error_message = "Use 2–60 lowercase letters, digits, or hyphens; begin/end with alphanumeric."
  }
}

variable "tags" {
  type        = map(string)
  description = "Additional cost and ownership tags; do not put secrets in tags."
  default     = {}
}
