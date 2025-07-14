# Use resource blocks to define components of your infrastructure. 
# A resource might be a physical component such as a server, or 
# it can be a logical resource such as a Heroku application.

# Resource blocks have two strings before the block: the resource
# type and the resource name. In this example, the resource type
# is azurerm_resource_group and the name is rg. The prefix of the
# type maps to the name of the provider. In the example configuration, 
# Terraform manages the azurerm_resource_group resource with the 
# azurerm provider. Together, the resource type and resource name 
# form a unique ID for the resource. For example, the ID for your 
# network is azurerm_resource_group.rg.

# Resource blocks contain arguments which you use to configure the
# resource. The Azure provider documentation documents supported 
# resources and their configuration options, including azurerm_resource_group 
# and its supported arguments.
resource "azurerm_resource_group" "rg" {
    name = "${var.project_name}rg"

    # update this a region you want
    location = "eastus"
}

data "azurerm_client_config" "current" {

}

resource "azurerm_key_vault" "kv" {
    name = "${var.project_name}kv"
    location = azurerm_resource_group.rg.location
    resource_group_name = azurerm_resource_group.rg.name
    tenant_id = data.azurerm_client_config.current.tenant_id
    
    enabled_for_disk_encryption = true
    soft_delete_retention_days = 7
    purge_protection_enabled = false

    sku_name = "standard"

    # access_policy {
    #     tenant_id = data.azurerm_client_config.current.tenant_id
    #     object_id = data.azurerm_client_config.current.object_id

    #     key_permissions = [
    #     "Get",
    #     ]

    #     secret_permissions = [
    #     "Get",
    #     ]

    #     storage_permissions = [
    #     "Get",
    #     ]
    # }
}

resource "azurerm_storage_account" "adls" {
    name = "${var.project_name}sa"
    resource_group_name = azurerm_resource_group.rg.name
    location = azurerm_resource_group.rg.location
    account_tier = "Standard"
    account_replication_type = "GRS"
    account_kind = "StorageV2"
    is_hns_enabled = "true"
    access_tier = "Cool"
}

resource "azurerm_storage_container" "containers" {
    # this just ensures that the for each argument has distinct values
    # because of the toset function which removes any duplicates
    for_each = toset(var.containers)
    name = "${var.project_name}sa-${each.value}"
    storage_account_name = "${var.project_name}sa"
    # storage_account_id = azurerm_storage_account.adls.id
    depends_on = [ azurerm_storage_account.adls ]
}