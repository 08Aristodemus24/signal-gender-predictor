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

* To run a Python ETL script in Azure Data Factory (ADF), you can use the following approaches:

Azure Batch: You can use Azure Batch to run your Python script in parallel on multiple virtual machines (VMs) to improve performance. This approach is suitable for large-scale data processing.
Azure Functions: You can use Azure Functions to run your Python script as a serverless function. This approach is suitable for small-scale data processing.
Azure Databricks: You can use Azure Databricks to run your Python script in a distributed environment. This approach is suitable for large-scale data processing and machine learning workloads.
When choosing the best approach for your specific use case, consider the following factors:

Data Volume: If you're processing a large volume of data, consider using Azure Batch or Azure Databricks.
Processing Time: If you need to process data quickly, consider using Azure Batch or Azure Databricks.
Cost: If you're looking for a cost-effective solution, consider using Azure Functions.
Complexity: If your ETL process is complex and requires advanced data processing capabilities, consider using Azure Databricks.

* In a machine learning ETL pipeline, it's generally recommended to split the data into training, validation, and testing sets before any data transformations or feature engineering that might be applied in the staging layer or later. This ensures that the splitting process is fair and doesn't introduce bias by using information from the entire dataset to influence the split. 
Why split early?
Preventing Data Leakage:
Splitting data before any transformations (like imputation, scaling, or encoding) ensures that the test set remains truly unseen. If you apply transformations to the entire dataset first and then split, you're essentially using information from the test set to influence those transformations, leading to an overly optimistic evaluation of the model's performance. 
Fair Evaluation:
Splitting the data before transformation allows you to accurately assess how well your model generalizes to new, unseen data. You can be confident that the evaluation metrics reflect the model's performance on data it hasn't been exposed to during training and transformation. 
Reproducibility:
Splitting data early and consistently allows for reproducible results. You can ensure that your experiments are repeatable by using the same split across multiple runs. 
ETL Pipeline Stages:
A typical ETL pipeline has several stages: 
Extraction: Data is pulled from various sources.
Transformation: Data is cleaned, normalized, and transformed into a suitable format for the model. This is where feature engineering might occur.
Loading: Transformed data is loaded into a data warehouse or data lake for storage and further analysis.
When to Split?
After extraction, but before any transformations:
This is the ideal point for splitting. You'll have the raw data in its original format, ready to be split into training, validation, and testing sets.
During or after staging, but before model training:
If you need to perform some transformations in the staging area, you can split the data after that. However, be mindful of the potential for data leakage and ensure that the transformations applied to the training set are also applied to the validation and test sets in a consistent manner. 
Example:
Imagine you're building a model to predict house prices. 
Extraction: You extract data from a real estate database.
Splitting: You split the data into training, validation, and test sets (e.g., 70/15/15 split).
Transformation: You perform feature engineering (e.g., creating new features like price per square foot) and data cleaning (e.g., imputing missing values) on the training set only. You then apply the same transformations to the validation and test sets.
Model Training: You train your model on the training set.
Model Evaluation: You evaluate the model's performance on the validation and test sets.
In essence, the core principle is to treat the test set as if it were truly "new" data that you're encountering for the first time when evaluating the model's performance. 

* The template deployment 'Microsoft.Web-FunctionApp-Portal-c54abcd7-9b54' is not valid according to the validation procedure. The tracking id is '4bbae7c4-8974-4168-987e-f54335884848'. See inner errors for details may occur in creating azure function

if this is the case it may be because the current location you chose does not reached the quota required for you to use the resource which int his case is the azure function. It may raise `This region has quota of 0 PremiumV2 cores for your subscription. Try selecting different region or SKU` which means you should select another region which may have this resource available

* 
```
resource "azurerm_resource_group" "example" {
  name     = "azure-functions-example-rg"
  location = "West Europe"
}

resource "azurerm_storage_account" "example" {
  name                     = "functionsappexamlpesa"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_app_service_plan" "example" {
  name                = "azure-functions-example-sp"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  kind                = "Linux"
  reserved            = true

  sku {
    tier = "Dynamic"
    size = "Y1"
  }

  lifecycle {
    ignore_changes = [
      kind
    ]
  }
}

resource "azurerm_function_app" "example" {
  name                       = "example-azure-function"
  location                   = azurerm_resource_group.example.location
  resource_group_name        = azurerm_resource_group.example.name
  app_service_plan_id        = azurerm_app_service_plan.example.id
  storage_account_name       = azurerm_storage_account.example.name
  storage_account_access_key = azurerm_storage_account.example.primary_access_key
  os_type                    = "linux"
  version                    = "~4"

  app_settings {
    FUNCTIONS_WORKER_RUNTIME = "python"
  }

  site_config {
    linux_fx_version = "python|3.9"
  }
}
```

* a function app resource requires a service plan which can be set to `consumption`, you need to download the azure resource extension and the azure functions extension in vs code. Login to your azure account via vs code in the accounts and tenants section, once done go to workspace, because we have already created our funciton app resource we can create the main individual function that we can deploy to this function app resource we created, parang siya yung tagahawak/manage ng mga function na gagawin mo na function. Save this function in your project directory named perhaps `azfunc` as this will contains the necessary files for your azure function. 

* installing the requirements.txt file after creating a local azure function 
```
(base) C:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor>.venv/Scripts/activate
'.venv' is not recognized as an internal or external command,
operable program or batch file.

(base) C:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor>cd .venv/Scripts/activate
The system cannot find the path specified.

(base) C:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor>python -m venv.venv/Scripts/activate
C:\Users\LARRY\anaconda3\python.exe: No module named venv.venv/Scripts/activate

(base) C:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor>python -m venv .venv/Scripts/activate

(base) C:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor>.venv/Scripts/activate.bat
'.venv' is not recognized as an internal or external command,
operable program or batch file.

(base) C:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor>/.venv/Scripts/activate.bat
The system cannot find the path specified.

(base) C:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor>azfunc/.venv/Scripts/activate.bat
'azfunc' is not recognized as an internal or external command,
operable program or batch file.

(base) C:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor>cd azfunc

(base) C:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc>venv/Scripts/activate.bat
'venv' is not recognized as an internal or external command,
operable program or batch file.

(base) C:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc>cd venv
The system cannot find the path specified.

(base) C:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc>cd .venv

(base) C:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc\.venv>./scripts/activate
'.' is not recognized as an internal or external command,
operable program or batch file.

(base) C:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc\.venv>./scripts/activate.bat
'.' is not recognized as an internal or external command,
operable program or batch file.

(base) C:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc\.venv>/scripts/activate.bat
The system cannot find the path specified.

(base) C:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc\.venv>cd scripts

(base) C:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc\.venv\Scripts>activate

(.venv) (base) C:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc\.venv\Scripts>cd ../..

(.venv) (base) C:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc>conda deactivate

(.venv) C:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc>pip install -r requirements.txt
Collecting azure-functions (from -r requirements.txt (line 5))
  Obtaining dependency information for azure-functions from https://files.pythonhosted.org/packages/68/ed/7555a93de73fb5743f9666c3673727b7b74e705fd278ea360ffe95559d5f/azure_functions-1.23.0-py3-none-any.whl.metadata
  Using cached azure_functions-1.23.0-py3-none-any.whl.metadata (7.3 kB)
Collecting werkzeug~=3.1.3 (from azure-functions->-r requirements.txt (line 5))
  Obtaining dependency information for werkzeug~=3.1.3 from https://files.pythonhosted.org/packages/52/24/ab44c871b0f07f491e5d2ad12c9bd7358e527510618cb1b803a88e986db1/werkzeug-3.1.3-py3-none-any.whl.metadata
  Using cached werkzeug-3.1.3-py3-none-any.whl.metadata (3.7 kB)
Collecting MarkupSafe>=2.1.1 (from werkzeug~=3.1.3->azure-functions->-r requirements.txt (line 5))
  Obtaining dependency information for MarkupSafe>=2.1.1 from https://files.pythonhosted.org/packages/da/b8/3a3bd761922d416f3dc5d00bfbed11f66b1ab89a0c2b6e887240a30b0f6b/MarkupSafe-3.0.2-cp311-cp311-win_amd64.whl.metadata
  Using cached MarkupSafe-3.0.2-cp311-cp311-win_amd64.whl.metadata (4.1 kB)
Using cached azure_functions-1.23.0-py3-none-any.whl (137 kB)
Using cached werkzeug-3.1.3-py3-none-any.whl (224 kB)
Using cached MarkupSafe-3.0.2-cp311-cp311-win_amd64.whl (15 kB)
Installing collected packages: MarkupSafe, werkzeug, azure-functions
Successfully installed MarkupSafe-3.0.2 azure-functions-1.23.0 werkzeug-3.1.3

[notice] A new release of pip is available: 23.2.1 -> 25.1.1
[notice] To update, run: python.exe -m pip install --upgrade pip
```

* PowerShell says "execution of scripts is disabled on this system." can be solved by Set-ExecutionPolicy RemoteSigned then reverting back to Set-ExecutionPolicy Restricted. If we check command execution policy via Get-ExecutionPolicy in Powershell (not CMD) we get Restricted

* debugging error when testing the azure function locally
``` 
func : The term 'func' is not recognized as the name of a cmdlet, function, script file, or operable program. Check the spelling of the name, or if 
a path was included, verify that the path is correct and try again.
At line:1 char:26
+ .venv\Scripts\activate ; func host start
```
is usually caused by lack of azure function core tools not being intalled in your system and the bin or scripts folder not part of the system or user environment variables. You can download the installer here which will automatically add it to the path system or user environment variables: https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-csharp

https://answers.microsoft.com/en-us/msoffice/forum/all/visual-studio-code-azure-function-error-as-the/540cc916-5005-4e57-aec8-def373402db1

but once this has finished debugging it will show us http://localhost:7071/api/http_trigger that we can go to to show that our azure function has been deployed locally, but to dpeloy this to azure function apps itself we need to go to our workspace > local roject > deploy to azure and select the azure function apps resource we created with specific service plans and all that etc.

* to stop azrure function from running locally go to task manager > details > find the func.exe running > end task

# Articles, Videos, Papers: 
* terraform tutorial for setting up azure services via code: https://developer.hashicorp.com/terraform/tutorials/azure-get-started/infrastructure-as-code
* end to end azure DE tutorial: https://www.youtube.com/watch?v=lyp8rlpJc3k&list=PLCBT00GZN_SAzwTS-SuLRM547_4MUHPuM&index=45&t=5222s
* after watching tutorial this is for magnifying your understanding to a typical DE project: https://www.youtube.com/watch?v=T8ahyYdSCGg