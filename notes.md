# Technologies:
* Azure databricks (Apache Spark) - for data transformation e.g. turning the raw signals into usable features e.g. through windowing and calculating features through each window
* Azure datafactory - for data task orchestration using a managed azure data factory with airlow
* Azure data lake - for storing data at each transformation step
* pinecone (or some kind of cloud vector database) - for storing the final calculated feature vectors in some kind of cloud feature vector storage
* Terraform - for automating setup of azure services/cloud infrastructure

# Insights:
* to set env variable in windows via CMd use `SETX <name of user env var> "<some value>"`
* install Azure cli by downloading installer at https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows?view=azure-cli-latest&pivots=msi

* 
```
(base) C:\Users\LARRY\Documents\Scripts>az account list
[
  {
    "cloudName": "AzureCloud",
    "homeTenantId": "<some home tenant id>",
    "id": "<some subscription id>",
    "isDefault": true,
    "managedByTenants": [],
    "name": "Azure subscription 1",
    "state": "Enabled",
    "tenantDefaultDomain": "<some email.onmicrosoft.com>",
    "tenantDisplayName": "Default Directory",
    "tenantId": "<some tenant id>",
    "user": {
      "name": "<your email used in azure>",
      "type": "user"
    }
  }
]
```

* coy the `subscription id` we listed earlier via az account list or from the az login command and now run `az ad sp create-for-rbac --role="Contributor" --scopes="/subscriptions/<SUBSCRIPTION_ID>"` which creates the equivalent of an IAM user in AWS which will output certain credentials we need to keep safe as this will be keys needed to access our azure services like azure data lake storage 

save these credentials as the ff. in an `.env` file or if possible create an azure key vault service which stores these credentials in the azures cloud

```
ARM_CLIENT_ID="<APPID_VALUE>"
ARM_CLIENT_SECRET="<PASSWORD_VALUE>"
ARM_SUBSCRIPTION_ID="<SUBSCRIPTION_ID>"
ARM_TENANT_ID="<TENANT_VALUE>"
```

* run `terraform init` to install azure provider otherwise it will throw 
```
Error: Missing required provider
│
│ This configuration requires provider registry.terraform.io/hashicorp/azurerm, but that provider isn't available. You
│ may be able to install it automatically by running:
│   terraform init
╵
```

* consistent formatting in all of your configuration files. The `terraform fmt` command automatically updates configurations in the current directory for readability and consistency.

Format your configuration. Terraform will print out the names of the files it modified, if any. In this case, your configuration file was already formatted correctly, so Terraform won't return any file names.

* You can also make sure your configuration is syntactically valid and internally consistent by using the `terraform validate` command.

Validate your configuration. The example configuration provided above is valid, so Terraform will return a success message.

* once initialization, formatting, and validation is done we can now creawte our azure service which in this case is a resouruce group via the terraform apply command which will reflect in our azure account itself when we visit it. From here we can name various resources ike azure data factory, azure data lake storage, etc. without hving to always click and manually setup these services via a UI

* 
```
{
    "sku": {
        "name": "Standard_RAGRS", // account_replication_type = "GRS"
        "tier": "Standard" // account_tier = "Standard"
    },
    "kind": "StorageV2", // account_kind = "StorageV2"
    "id": "/subscriptions/<some sub id>/resourceGroups/sgp_pipeline_rg/providers/Microsoft.Storage/storageAccounts/sgppipelinesa",
    "name": "sgppipelinesa",
    "type": "Microsoft.Storage/storageAccounts",
    "location": "eastus", // location = azurerm_resource_group.rg.location
    "tags": {},
    "properties": {
        "dnsEndpointType": "Standard",
        "defaultToOAuthAuthentication": false,
        "publicNetworkAccess": "Enabled",
        "keyCreationTime": {
            "key1": "2025-07-14T05:48:49.3540428Z",
            "key2": "2025-07-14T05:48:49.3540428Z"
        },
        "allowCrossTenantReplication": false, // allow_cross_tenant_replication = "false"
        "privateEndpointConnections": [],
        "isSftpEnabled": false, // is_sftp_enabled = "false"
        "minimumTlsVersion": "TLS1_2", // minimum_tls_version
        "allowBlobPublicAccess": false, // allow_blob_public_access = "false"
        "allowSharedKeyAccess": true, 
        "largeFileSharesState": "Enabled",
        "isHnsEnabled": true, // is_hns_enabled = "true" which is the enable heirarchical name space option 
        "networkAcls": {
            "bypass": "AzureServices",
            "virtualNetworkRules": [],
            "ipRules": [],
            "defaultAction": "Allow"
        },
        "supportsHttpsTrafficOnly": true,
        "encryption": {
            "requireInfrastructureEncryption": false,
            "services": {
                "file": {
                    "keyType": "Account",
                    "enabled": true,
                    "lastEnabledTime": "2025-07-14T05:48:49.3540428Z"
                },
                "blob": {
                    "keyType": "Account",
                    "enabled": true,
                    "lastEnabledTime": "2025-07-14T05:48:49.3540428Z"
                }
            },
            "keySource": "Microsoft.Storage"
        },
        "accessTier": "Cool", // access_tier = "Cool"
        "provisioningState": "Succeeded",
        "creationTime": "2025-07-14T05:48:49.1665344Z",
        "primaryEndpoints": {
            "dfs": "https://sgppipelinesa.dfs.core.windows.net/",
            "web": "https://sgppipelinesa.z13.web.core.windows.net/",
            "blob": "https://sgppipelinesa.blob.core.windows.net/",
            "queue": "https://sgppipelinesa.queue.core.windows.net/",
            "table": "https://sgppipelinesa.table.core.windows.net/",
            "file": "https://sgppipelinesa.file.core.windows.net/"
        },
        "primaryLocation": "eastus",
        "statusOfPrimary": "available",
        "secondaryLocation": "westus",
        "statusOfSecondary": "available",
        "secondaryEndpoints": {
            "dfs": "https://sgppipelinesa-secondary.dfs.core.windows.net/",
            "web": "https://sgppipelinesa-secondary.z13.web.core.windows.net/",
            "blob": "https://sgppipelinesa-secondary.blob.core.windows.net/",
            "queue": "https://sgppipelinesa-secondary.queue.core.windows.net/",
            "table": "https://sgppipelinesa-secondary.table.core.windows.net/"
        }
    },
    "apiVersion": "2022-05-01"
}
```

in full detail the adl2 resource can have this many arguments rather than just `account_kind`, `account_replication_type`, `account_tier`, `is_hns_enabled`, `location`, `resource_group_name`
```
    + access_tier                       = (known after apply)
      + account_kind                      = "StorageV2"
      + account_replication_type          = "GRS"
      + account_tier                      = "Standard"
      + allow_nested_items_to_be_public   = true
      + enable_https_traffic_only         = true
      + id                                = (known after apply)
      + infrastructure_encryption_enabled = false
      + is_hns_enabled                    = true
      + large_file_share_enabled          = (known after apply)
      + location                          = "eastus"
      + min_tls_version                   = "TLS1_2"
      + name                              = "sgppipelinesa"
      + nfsv3_enabled                     = false
      + primary_access_key                = (sensitive value)
      + primary_blob_connection_string    = (sensitive value)
      + primary_blob_endpoint             = (known after apply)
      + primary_blob_host                 = (known after apply)
      + primary_connection_string         = (sensitive value)
      + primary_dfs_endpoint              = (known after apply)
      + primary_dfs_host                  = (known after apply)
      + primary_file_endpoint             = (known after apply)
      + primary_file_host                 = (known after apply)
      + primary_location                  = (known after apply)
      + primary_queue_endpoint            = (known after apply)
      + primary_queue_host                = (known after apply)
      + primary_table_endpoint            = (known after apply)
      + primary_table_host                = (known after apply)
      + primary_web_endpoint              = (known after apply)
      + primary_web_host                  = (known after apply)
      + queue_encryption_key_type         = "Service"
      + resource_group_name               = "SGPPipeResourceGroup"
      + secondary_access_key              = (sensitive value)
      + secondary_blob_connection_string  = (sensitive value)
      + secondary_blob_endpoint           = (known after apply)
      + secondary_blob_host               = (known after apply)
      + secondary_connection_string       = (sensitive value)
      + secondary_dfs_endpoint            = (known after apply)
      + secondary_dfs_host                = (known after apply)
      + secondary_file_endpoint           = (known after apply)
      + secondary_file_host               = (known after apply)
      + secondary_location                = (known after apply)
      + secondary_queue_endpoint          = (known after apply)
      + secondary_queue_host              = (known after apply)
      + secondary_table_endpoint          = (known after apply)
      + secondary_table_host              = (known after apply)
      + secondary_web_endpoint            = (known after apply)
      + secondary_web_host                = (known after apply)
      + shared_access_key_enabled         = true
      + table_encryption_key_type         = "Service"

      + blob_properties (known after apply)

      + network_rules (known after apply)

      + queue_properties (known after apply)

      + routing (known after apply)

      + share_properties (known after apply)
```



# Articles, Videos, Papers:
* terraform tutorial for setting up azure services via code: https://developer.hashicorp.com/terraform/tutorials/azure-get-started/infrastructure-as-code
* end to end azure DE tutorial: https://www.youtube.com/watch?v=lyp8rlpJc3k&list=PLCBT00GZN_SAzwTS-SuLRM547_4MUHPuM&index=45&t=5222s
* after watching tutorial this is for magnifying your understanding to a typical DE project: https://www.youtube.com/watch?v=T8ahyYdSCGg