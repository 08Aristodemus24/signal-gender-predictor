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
module "test_module" {
  source = "./test_module"
}

resource "azurerm_resource_group" "rg" {
  name = "${var.project_name}rg"

  # update this a region you want
  location = "eastus"
}

data "azurerm_client_config" "current" {

}

resource "azurerm_key_vault" "kv" {
  name                        = "${var.project_name}kv"
  location                    = azurerm_resource_group.rg.location
  resource_group_name         = azurerm_resource_group.rg.name
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  enabled_for_disk_encryption = true
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false
  sku_name                    = "standard"

  # this is imperative to add as we need to be able to
  # get, create, and delete keys and secret keys
  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id

    # this is just a workaround as principal id not object id from
    # azure rm client config does works over the latter
    object_id = module.test_module.principal_id

    key_permissions = [
      "Get",
      "Create",
      "Update",
      "Import",
      "Delete",
    ]

    secret_permissions = [
      "Get",
      "List",
      "Set",
      "Delete"
    ]

    storage_permissions = [
      "Get",
    ]
  }

  # we want our permission model to be 'vault access policy'
  # not 'role based access control (RBAC)'
  enable_rbac_authorization = false
}

# azure data lake storage for each staging layer in pipeline
resource "azurerm_storage_account" "adls" {
  name                     = "${var.project_name}sa"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  account_kind             = "StorageV2"

  # so we can work other services like azure ML because
  # the latter does not use a storage account with heirarchical
  # namespace enableds
  is_hns_enabled = "false"
  access_tier    = "Cool"
}

# azure containers for data lake storage 
resource "azurerm_storage_container" "containers" {
  # this just ensures that the for each argument has distinct values
  # because of the toset function which removes any duplicates
  for_each             = toset(var.containers)
  name                 = "${var.project_name}sa-${each.value}"
  storage_account_name = "${var.project_name}sa"
  depends_on           = [azurerm_storage_account.adls]
  # storage_account_id = azurerm_storage_account.adls.id

}

# azure databricks workspace for transforming data at each staging layer
resource "azurerm_databricks_workspace" "dbw" {
  name                = "${var.project_name}dbws"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  # not standard because we need the unity catalog access connector
  sku = "premium"

  tags = {
    Environment = "development"
  }
}

# azure data factory for orchestrating the whole workflow from extraction
# transformation and to loading
resource "azurerm_data_factory" "adf" {
  name                = "${var.project_name}adf"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}