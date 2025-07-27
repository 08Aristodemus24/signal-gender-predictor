resource "azurerm_user_assigned_identity" "uai" {
  location            = "eastus"
  name                = "${var.project_name}uai"
  resource_group_name = "${var.project_name}rg"

  # depends_on           = [ azurerm_resource_group.rg ]
}

output "principal_id" {
  value       = azurerm_user_assigned_identity.uai.principal_id
  description = "Set accordingly or from terraform documentation"
}