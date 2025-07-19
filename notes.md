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

save these credentials as the ff. in an `.env` file or if possible create an azure key vault service which stores these credentials in the azure cloud

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

* to activate the venv environment relatively specifically in a windows machine you need to use backslashes instead of forward slashes e.g. if were currently in root directory where azfunc folder is and we run `azfunc/.venv/scripts/activate.bat` this will not work, but running `azfunc\.venv\Scripts\activate.bat` in the command line will

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

* add this in order to solve `No job functions found.` error add `"AzureWebJobsFeatureFlags": "EnableWorkerIndexing"` in your local.settings.json file

* another is Exception: SyntaxError: (unicode error) 'unicodeescape' azure funciton python which can be solved by using forward slashes in potential strings instead, using `\\` or `r"\"` 

* once you deploy your function may raise an `Error: {"message":"Failed to fetch","stack":"TypeError: Failed to fetch\n    at https://portal.azure.com/Content/Dynamic/EueNcQE5D-tA.js:177:24220\n    at https://portal.azure.com/Content/Dynamic/EueNcQE5D-tA.js:177:24441\n    at nt (https://portal.azure.com/Content/Dynamic/EueNcQE5D-tA.js:177:7009)\n    at https://portal.azure.com/Content/Dynamic/EueNcQE5D-tA.js:177:10885\n    at Array.forEach (<anonymous>)\n    at https://portal.azure.com/Content/Dynamic/EueNcQE5D-tA.js:177:10873\n    at Object.nt (https://portal.azure.com/Content/Dynamic/EueNcQE5D-tA.js:177:7009)\n    at b (https://portal.azure.com/Content/Dynamic/EueNcQE5D-tA.js:60:2039)\n    at v (https://portal.azure.com/Content/Dynamic/EueNcQE5D-tA.js:60:1870)","isError":true}` which maybe due to `Cross Origin Resource Sharing` problems

* in full detail the `azurerm_databricks_workspace` has the followign arguments that can be supplied
```
      ...
      + customer_managed_key_enabled          = false
      + id                                    = (known after apply)
      + infrastructure_encryption_enabled     = false
      + location                              = "eastus"
      + managed_resource_group_id             = (known after apply)
      + managed_resource_group_name           = (known after apply)
      + name                                  = "sgppipelinedbws"
      + network_security_group_rules_required = (known after apply)
      + public_network_access_enabled         = true
      + resource_group_name                   = "sgppipelinerg"
      + sku                                   = "standard"
      + storage_account_identity              = (known after apply)
      + tags                                  = {
          + "Environment" = "development"
        }
      + workspace_id                          = (known after apply)
      + workspace_url                         = (known after apply)

      + custom_parameters (known after apply)
    }
```

* for `azurerm_data_factory` it has the following arguments
```
      + id                     = (known after apply)
      + location               = "eastus"
      + name                   = "sgppipelineadf"
      + public_network_enabled = true
      + resource_group_name    = "sgppipelinerg" 
```

* the most likely reason why you are still encoutnering a code 500 internal server error even when you've added `*`, `https://portal.azure.com`, `https://functions.azure.com`, `https://*.com`, and `http://*.com` is because you maybe using a relative module inside your `function_app.py` that has not been included in deployment. https://stackoverflow.com/questions/68009769/azure-function-500-internal-internal-server-error-in-run-test-mode


Okay, an "Internal Server Error" (HTTP 500) in a deployed Azure Function, especially when it works fine locally, is a very common scenario. The fact that your function extract_signals depends on a relative import called download which targets the local machine is a huge red flag and almost certainly the cause of your problem.

Let's break down why this is happening and how to fix it:

Why It Works Locally but Fails on Azure
Local Environment: When you run func host start locally, your Python code runs within your local machine's environment. The download module (which you described earlier as downloading files to your local machine, not ADLS) functions perfectly because it has access to your local filesystem.

Azure Cloud Environment:

Serverless Nature: When your Azure Function is deployed, it runs in a serverless environment in the cloud. It doesn't have "your local machine" to download to.

Ephemeral Storage: While Azure Functions do have some temporary, ephemeral storage, it's not persistent, it's limited in size, and you cannot rely on it as a destination for downloaded files that need to be further processed or stored long-term.

No Local File System Access (as you expect): Your function code tries to write to a path like C:\Users\LARRY\... or /tmp/... which doesn't exist or isn't accessible in the way your local machine's filesystem is.

Permissions: Even if a temporary path existed, the function might not have the necessary permissions to write to arbitrary locations on the host's underlying infrastructure.

The "Internal Server Error" (HTTP 500):
When your download module tries to write to a non-existent or inaccessible local path in the Azure environment, it encounters an I/O error (e.g., "permission denied," "no such directory," "disk full"). This unhandled error then propagates up and manifests as a generic "Internal Server Error" to the caller of your HTTP trigger.

CORS is Not the Issue Here
You mentioned configuring CORS. CORS (Cross-Origin Resource Sharing) errors happen when a web browser tries to make a request to an API on a different domain than the one the web page originated from, and the API server doesn't explicitly allow it. An Internal Server Error (500) indicates a problem within your function's code execution on the server side, not a client-side access restriction due to CORS. So, while CORS is important for your Flask app later, it's not the cause of this 500 error.

How to Fix It (The Solution You Already Identified!)
This is precisely why we discussed downloading the files directly to Azure Data Lake Storage Gen2 (ADLS Gen2) instead of your local machine.

Your download module (or whatever function is responsible for this) needs to be rewritten to:

Accept the download URL.

Use requests to get the file content.

**Use azure-storage-blob (or azure.storage.filedatalake for ADLS Gen2-specific operations, though azure-storage-blob is generally sufficient and more common for basic file operations on ADLS Gen2) to upload that content directly to your specified ADLS Gen2 container (your "Bronze" layer).

Key Changes Needed:

Modify download.py (or the relevant module):

Remove any code that writes to a local file path.

Import BlobServiceClient from azure.storage.blob.

Implement the logic to authenticate with ADLS Gen2 (preferably via Managed Identity when deployed).

Implement the upload_blob method to stream the downloaded content directly to ADLS.

Update requirements.txt: Make sure azure-storage-blob and azure-identity (if using Managed Identity) are listed.

Ensure ADLS Gen2 Access:

Deployed Function: If you're using Managed Identity, ensure your Azure Function App's Managed Identity has been granted the necessary RBAC roles on your ADLS Gen2 account (e.g., "Storage Blob Data Contributor" role on the target container).

Local Development: Make sure your local.settings.json has the necessary environment variables for you

* an error occured creating the secret <key> may occur when creating a key in azure key vault. It may have something to do with your permission policies. Tied to this is another error which is object_id is not a valid UUID https://stackoverflow.com/questions/75107879/error-key-vault-object-id-is-an-invalid-uuid-terraform-azure



- if `operation not allowed by RBAC. If role assignments were recently changed pelase wait several minutes for role assignments to become effective` occurs you need to make sure that in the `access control tab` in the `resource groups > <resource group> > <your azure key vault resource>` click `view my access` and make sure key vualt administrator is a part of those role assignments, if not create one. by navigating again to main `<azure key vault resource> > access control tab` and then click add role assignment

- if `operation "List" is not enabled in this key vault's access policy` occurs it is most likely because our principal is an application type because note that when key vault is created by terraform or by any azure service such as Azure ML workspace, it contains access policies assigned to only to said workspace or by the application terraform created which is why it is set to an (application type) and not a user type. Solution to this is to go to access control, add role assignment, search for `key vault administrator` role and add this role to your service principal tied to your account

To resolve the error, you need to create another vault access policy by adding required permissions such as `create`, `set`, `delete` etc. and assign it to signed-in user account which is the azure account email you are using

* we could actually setup as part of our infrastructure our databricks cluster that we will be using for our notebooks (we dont reate noteooks sa part of our infrastructure because we don't want it to be a part of the destruction process when we tear down the infrastructure when not in use). We just need to list databricks as part of our providers since it is not a part of the azure ecosystem per se. 
```
data "databricks_node_type" "smallest" {
  local_disk = true
}

data "databricks_spark_version" "latest_lts" {
  long_term_support = true
}

resource "databricks_cluster" "shared_autoscaling" {
  cluster_name            = "Shared Autoscaling"
  spark_version           = data.databricks_spark_version.latest_lts.id
  node_type_id            = data.databricks_node_type.smallest.id
  autotermination_minutes = 20
  autoscale {
    min_workers = 1
    max_workers = 50
  }
}
```

* uploading a file via python to azure data lake storage container errors:
- HttpResponseError: This request is not authorized to perform this operation using this permission. 
- ErrorCode:AuthorizationPermissionMismatch

could be caused:

- by not being able to grant access control to the azure data lake storage account like we did when we were granting access to an S3 bucket 
```
I found it's not enough for the app and account to be added as owners. I would go into your storage account > IAM > Add role assignment, and add the special permissions for this type of request:

- Storage Blob Data Contributor
- Storage Queue Data Contributor
```

to add IAM policy
to add principal owner
to add access control 

ok so can't do a get request and can't do a post request which is what I'm doiong reading from the azure data lake storage container, and

- could be because of the fact that anonymous access level is set to private
- access control list has security principals like superuser to have read, write, and execute
- no access policy is set 

remember we created a microsoft entra id which is what you can use to authorize a BlobServiceClient object. Ito yung service principal na sinasabi which is a type of security principal among others (e.g. service principal, user identity, managed identity) which is typically invoked using a local script that runs the statements that upload to azure data lake storage 

we need to figure out a way how to authenticate using the service priincipal id we created when we tried to setup terraform with azure via the `az login`, `az account set --subscription "<your subscription id after logging qith your email via az login>"`, and `az ad sp create-for-rbac --role="Contributor" --scopes="/subscriptions/<SUBSCRIPTION_ID>"` which finally creates our service principal

[this](https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/local-development-service-principal?tabs=azure-portal) essentially takes us right after we create our microsoft entra id (formeerly azure active directory) via `az ad sp create-for-rbac --role="Contributor" --scopes="/subscriptions/<SUBSCRIPTION_ID>"` where az, ad, and sp here just mean azure, active directory, and service principal respectively and outlines that we have to assign roles/permissions to our application (the script or python script that will read, write, update, delete azure resources programmatically)

- another cause could be because Gen2 lakes do not have containers, they have filesystems (which are a very similiar concept).

On your storage account have you enabled the "Hierarchical namespace" feature? You can see this in the Configuration blade of the Storage account. If you have then the storage account is a Lake Gen2 - if not it is simply a blob storage account and you need to follow the instructions for using blob storage.

Assuming you have set that feature then you can see the FileSystems blade - in there you create file systems, in a very similar way to blob containers. This is the name you need at the start of your abfss URL.

However, the error message you have indicates to me that your service principal does not have permission on the data lake. You should either grant permission using a RBAC role on the storage account resource (add to storage account contributors or readers). Or use Storage Explorer to grant permission at a more granular level.

Remember that data lake requires execute permissions on every folder from root to the folder you are trying to read/write from. As a test try reading a file from root first.

solution is maybe to make an azure data lake storage account with heirarchical namespace argument set to false

- another could be because the storage account container itself indicates `Authentication method: Access key(Switch to Microsoft Entra user account)` and if we click this switch it shows an error that we `do not have permissions to list the data using your user account with Microsoft Entra ID`. This is because we have not assigned the resource or resource group an IAM role with the service principal as the role so it is imperative that we add it in order to get rid of this error

we can actually set this manually during the creation of our storage acccount so we don't have to always swith between using 

```
Environment is configured for ClientSecretCredential

[2025-07-18T14:25:01.126Z] ManagedIdentityCredential will use IMDS with client_id: <some code>

[2025-07-18T14:25:01.143Z] Request URL: 'https://login.microsoftonline.com/<some code>/v2.0/.well-known/openid-configuration'
Request method: 'GET'
Request headers:
    'User-Agent': 'azsdk-python-identity/1.23.1 Python/3.11.5 (Windows-10-10.0.26100-SP0)'
No body was attached to the request
[2025-07-18T14:25:01.439Z] Response status: 200

Response headers:
    'Cache-Control': 'max-age=86400, private'
    'Content-Type': 'application/json; charset=utf-8'
    'Strict-Transport-Security': 'REDACTED'
    'X-Content-Type-Options': 'REDACTED'
    'Access-Control-Allow-Origin': 'REDACTED'
    'Access-Control-Allow-Methods': 'REDACTED'
    'P3P': 'REDACTED'
    'x-ms-request-id': '<some code>'
    'x-ms-ests-server': 'REDACTED'
    'x-ms-srs': 'REDACTED'
    'Content-Security-Policy-Report-Only': 'REDACTED'
    'X-XSS-Protection': 'REDACTED'
    'Set-Cookie': 'REDACTED'
    'Date': 'Fri, 18 Jul 2025 14:24:59 GMT'
    'Content-Length': '1753'

[2025-07-18T14:25:01.483Z] Request URL: 'https://login.microsoftonline.com/<some code>/oauth2/v2.0/token'
Request method: 'POST'
Request headers:
    'Accept': 'application/json'
    'x-client-sku': 'REDACTED'
    'x-client-ver': 'REDACTED'
    'x-client-os': 'REDACTED'
    'x-ms-lib-capability': 'REDACTED'
    'client-request-id': 'REDACTED'
    'x-client-current-telemetry': 'REDACTED'
    'x-client-last-telemetry': 'REDACTED'
    'User-Agent': 'azsdk-python-identity/1.23.1 Python/3.11.5 (Windows-10-10.0.26100-SP0)'
A body is sent with the request
[2025-07-18T14:25:01.614Z] Response status: 200

Response headers:
    'Cache-Control': 'no-store, no-cache'
    'Pragma': 'no-cache'
    'Content-Type': 'application/json; charset=utf-8'
    'Expires': '-1'
    'Strict-Transport-Security': 'REDACTED'
    'X-Content-Type-Options': 'REDACTED'
    'P3P': 'REDACTED'
    'client-request-id': 'REDACTED'
    'x-ms-request-id': '<some code>'
    'x-ms-ests-server': 'REDACTED'
    'x-ms-clitelem': 'REDACTED'
    'x-ms-srs': 'REDACTED'
    'Content-Security-Policy-Report-Only': 'REDACTED'
    'X-XSS-Protection': 'REDACTED'
    'Set-Cookie': 'REDACTED'
    'Date': 'Fri, 18 Jul 2025 14:24:59 GMT'
    'Content-Length': '1628'

[2025-07-18T14:25:01.629Z] DefaultAzureCredential acquired a token from EnvironmentCredential

[2025-07-18T14:25:01.636Z] Request URL: 'https://sgppipelinesa.blob.core.windows.net/sgppipelinesa-bronze?restype=REDACTED&comp=REDACTED'
Request method: 'GET'
Request headers:
    'x-ms-version': 'REDACTED'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.26.0 Python/3.11.5 (Windows-10-10.0.26100-SP0)'
    'x-ms-date': 'REDACTED'
    'x-ms-client-request-id': '<some code>'
    'Authorization': 'REDACTED'
No body was attached to the request
[2025-07-18T14:25:02.725Z] Response status: 403
```

```
[2025-07-19T04:36:27.231Z] Request URL: 'https://login.microsoftonline.com/<some code>/v2.0/.well-known/openid-configuration'
Request method: 'GET'
Request headers:
    'User-Agent': 'azsdk-python-identity/1.23.1 Python/3.11.5 (Windows-10-10.0.26100-SP0)'
No body was attached to the request
[2025-07-19T04:36:28.756Z] Response status: 200
Response headers:
    'Cache-Control': 'max-age=86400, private'
    'Content-Type': 'application/json; charset=utf-8'
    'Strict-Transport-Security': 'REDACTED'
    'X-Content-Type-Options': 'REDACTED'
    'Access-Control-Allow-Origin': 'REDACTED'
    'Access-Control-Allow-Methods': 'REDACTED'
    'P3P': 'REDACTED'
    'x-ms-request-id': '<some code>'
    'x-ms-ests-server': 'REDACTED'
    'x-ms-srs': 'REDACTED'
    'Content-Security-Policy-Report-Only': 'REDACTED'
    'X-XSS-Protection': 'REDACTED'
    'Set-Cookie': 'REDACTED'
    'Date': 'Sat, 19 Jul 2025 04:36:27 GMT'
    'Content-Length': '1753'



[2025-07-19T04:36:28.781Z] Request URL: 'https://login.microsoftonline.com/<some code>/oauth2/v2.0/token'
Request method: 'POST'
Request headers:
    'Accept': 'application/json'
    'x-client-sku': 'REDACTED'
    'x-client-ver': 'REDACTED'
    'x-client-os': 'REDACTED'
    'x-ms-lib-capability': 'REDACTED'
    'client-request-id': 'REDACTED'
    'x-client-current-telemetry': 'REDACTED'
    'x-client-last-telemetry': 'REDACTED'
    'User-Agent': 'azsdk-python-identity/1.23.1 Python/3.11.5 (Windows-10-10.0.26100-SP0)'
A body is sent with the request
[2025-07-19T04:36:29.114Z] Response status: 200
Response headers:
    'Cache-Control': 'no-store, no-cache'
    'Pragma': 'no-cache'
    'Content-Type': 'application/json; charset=utf-8'
    'Expires': '-1'
    'Strict-Transport-Security': 'REDACTED'
    'X-Content-Type-Options': 'REDACTED'
    'P3P': 'REDACTED'
    'client-request-id': 'REDACTED'
    'x-ms-request-id': '<some code>'
    'x-ms-ests-server': 'REDACTED'
    'x-ms-clitelem': 'REDACTED'
    'x-ms-srs': 'REDACTED'
    'Content-Security-Policy-Report-Only': 'REDACTED'
    'X-XSS-Protection': 'REDACTED'
    'Set-Cookie': 'REDACTED'
    'Date': 'Sat, 19 Jul 2025 04:36:27 GMT'
    'Content-Length': '1628'



[2025-07-19T04:36:29.120Z] DefaultAzureCredential acquired a token from EnvironmentCredential
[2025-07-19T04:36:29.121Z] Request URL: 'https://sgppipelinesa.blob.core.windows.net/sgppipelinesa-bronze?restype=REDACTED&comp=REDACTED'
Request method: 'GET'
Request headers:
    'x-ms-version': 'REDACTED'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.26.0 Python/3.11.5 (Windows-10-10.0.26100-SP0)'
    'x-ms-date': 'REDACTED'
    'x-ms-client-request-id': 'some code>'
    'Authorization': 'REDACTED'
No body was attached to the request
[2025-07-19T04:36:30.825Z] Response status: 403
Response headers:
    'Content-Length': '279'
    'Content-Type': 'application/xml'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-request-id': 'some code>'
    'x-ms-client-request-id': 'some code>'
    'x-ms-version': 'REDACTED'
    'x-ms-error-code': 'AuthorizationPermissionMismatch'
    'Date': 'Sat, 19 Jul 2025 04:36:30 GMT'
```

- *switch authentication method from access key to entra user account which is where the service principal is under*

I understand that you are getting AuthorizationPermissionMismatch error when attempting to access a blob file in Azure Blob Storage which might be due to insufficient permissions and below are some troubleshooting steps to overcome this error,

- Make sure the user or application has the necessary permissions/access to the blob storage assigned: Assign an Azure role for access to blob data and listed under service principal of IAM Access.
- Check the access policies for the blob container and confirm that your IP address is added to the CORS (Cross-Origin Resource Sharing) settings on the blob storage. This ensures that your requests are allowed from the specified IP.
- When a user is part of a group, Azure evaluates permissions based on both direct and inherited roles. Ensure that the group itself has the necessary permissions on the blob storage and check if there are conflicting roles assigned directly to the user or application. Sometimes, a direct role assignment can override an inherited role from a group.
- Use the Effective Permissions tool in the Azure portal to see the combined permissions for a user or application. It considers both direct and inherited roles.
- Make sure you’ve properly configured your BlobServiceClient and that the container and blob names are correct.
- Try using "Diagnose and solve problems" tool in the Azure portal sidebar for your storage account. It will help you look through your logs to see what's going on.

- I've tried running `az storage blob list --account-name sgppipelinesa --container-name sgppipelinesa-bronze` using the azure CLI and it returns the files in the ADLS container the way I want to:
```
[
  {
    "container": "sgppipelinesa-bronze",
    "content": "",
    "deleted": null,
    "encryptedMetadata": null,
    "encryptionKeySha256": null,
    "encryptionScope": null,
    "hasLegalHold": null,
    "hasVersionsOnly": null,
    "immutabilityPolicy": {
      "expiryTime": null,
      "policyMode": null
    },
    "isAppendBlobSealed": null,
    "isCurrentVersion": null,
    "lastAccessedOn": null,
    "metadata": {},
    "name": "1028-20100710-hne/LICENSE",
    "objectReplicationDestinationPolicy": null,
    "objectReplicationSourceProperties": [],
    "properties": {
      "appendBlobCommittedBlockCount": null,
      "blobTier": "Cool",
      "blobTierChangeTime": null,
      "blobTierInferred": true,
      "blobType": "BlockBlob",
      "contentLength": 659,
      "contentRange": null,
      "contentSettings": {
        "cacheControl": null,
        "contentDisposition": null,
        "contentEncoding": null,
        "contentLanguage": null,
        "contentMd5": "hYttkX+po5nJ2C4133I3MA==",
        "contentType": "application/octet-stream"
      },
      "copy": {
        "completionTime": null,
        "destinationSnapshot": null,
        "id": null,
        "incrementalCopy": null,
        "progress": null,
        "source": null,
        "status": null,
        "statusDescription": null
      },
      "creationTime": "2025-07-19T06:11:38+00:00",
      "deletedTime": null,
      "etag": "0x8DDC68B1F91D8DC",
      "lastModified": "2025-07-19T06:11:38+00:00",
      "lease": {
        "duration": null,
        "state": "available",
        "status": "unlocked"
      },
      "pageBlobSequenceNumber": null,
      "pageRanges": null,
      "rehydrationStatus": null,
      "remainingRetentionDays": null,
      "serverEncrypted": true
    },
    "rehydratePriority": null,
    "requestServerEncrypted": null,
    "snapshot": null,
    "tagCount": null,
    "tags": null,
    "versionId": null
  },
  {
    "container": "sgppipelinesa-bronze",
    "content": "",
    "deleted": null,
    "encryptedMetadata": null,
    "encryptionKeySha256": null,
    "encryptionScope": null,
    "hasLegalHold": null,
    "hasVersionsOnly": null,
    "immutabilityPolicy": {
      "expiryTime": null,
      "policyMode": null
    },
    "isAppendBlobSealed": null,
    "isCurrentVersion": null,
    "lastAccessedOn": null,
    "metadata": {},
    "name": "1028-20100710-hne/etc/GPL_license.txt",
    "objectReplicationDestinationPolicy": null,
    "objectReplicationSourceProperties": [],
    "properties": {
      "appendBlobCommittedBlockCount": null,
      "blobTier": "Cool",
      "blobTierChangeTime": null,
      "blobTierInferred": true,
      "blobType": "BlockBlob",
      "contentLength": 35147,
      "contentRange": null,
      "contentSettings": {
        "cacheControl": null,
        "contentDisposition": null,
        "contentEncoding": null,
        "contentLanguage": null,
        "contentMd5": "mRjydU5hdYhK0lv7QrYNPg==",
        "contentType": "text/plain"
      },
      "copy": {
        "completionTime": null,
        "destinationSnapshot": null,
        "id": null,
        "incrementalCopy": null,
        "progress": null,
        "source": null,
        "status": null,
        "statusDescription": null
      },
      "creationTime": "2025-07-19T06:11:38+00:00",
      "deletedTime": null,
      "etag": "0x8DDC68B1F63A3A8",
      "lastModified": "2025-07-19T06:11:38+00:00",
      "lease": {
        "duration": null,
        "state": "available",
        "status": "unlocked"
      },
      "pageBlobSequenceNumber": null,
      "pageRanges": null,
      "rehydrationStatus": null,
      "remainingRetentionDays": null,
      "serverEncrypted": true
    },
    "rehydratePriority": null,
    "requestServerEncrypted": null,
    "snapshot": null,
    "tagCount": null,
    "tags": null,
    "versionId": null
  },
  ...
  {
    "container": "sgppipelinesa-bronze",
    "content": "",
    "deleted": null,
    "encryptedMetadata": null,
    "encryptionKeySha256": null,
    "encryptionScope": null,
    "hasLegalHold": null,
    "hasVersionsOnly": null,
    "immutabilityPolicy": {
      "expiryTime": null,
      "policyMode": null
    },
    "isAppendBlobSealed": null,
    "isCurrentVersion": null,
    "lastAccessedOn": null,
    "metadata": {},
    "name": "1028-20100710-hne/wav/rp-31.wav",
    "objectReplicationDestinationPolicy": null,
    "objectReplicationSourceProperties": [],
    "properties": {
      "appendBlobCommittedBlockCount": null,
      "blobTier": "Cool",
      "blobTierChangeTime": null,
      "blobTierInferred": true,
      "blobType": "BlockBlob",
      "contentLength": 132044,
      "contentRange": null,
      "contentSettings": {
        "cacheControl": null,
        "contentDisposition": null,
        "contentEncoding": null,
        "contentLanguage": null,
        "contentMd5": "JRxrYCMjpT3pWBCMkaeCtg==",
        "contentType": "audio/wav"
      },
      "copy": {
        "completionTime": null,
        "destinationSnapshot": null,
        "id": null,
        "incrementalCopy": null,
        "progress": null,
        "source": null,
        "status": null,
        "statusDescription": null
      },
      "creationTime": "2025-07-19T06:11:42+00:00",
      "deletedTime": null,
      "etag": "0x8DDC68B21AB90F9",
      "lastModified": "2025-07-19T06:11:42+00:00",
      "lease": {
        "duration": null,
        "state": "available",
        "status": "unlocked"
      },
      "pageBlobSequenceNumber": null,
      "pageRanges": null,
      "rehydrationStatus": null,
      "remainingRetentionDays": null,
      "serverEncrypted": true
    },
    "rehydratePriority": null,
    "requestServerEncrypted": null,
    "snapshot": null,
    "tagCount": null,
    "tags": null,
    "versionId": null
  }
]
```

this time nung tinanggal ko yung pycache inside the azure function app folder and commented storage account in the .env file out to see if DefaultAzureCredential will change reading it I got now a 402 http error which is a resource requires payment code
```
[2025-07-19T06:27:23.661Z] Request URL: 'https://login.microsoftonline.com/some code>/v2.0/.well-known/openid-configuration'
Request method: 'GET'
Request headers:
    'User-Agent': 'azsdk-python-identity/1.23.1 Python/3.11.5 (Windows-10-10.0.26100-SP0)'
No body was attached to the request
[2025-07-19T06:27:25.029Z] Response status: 200
Response headers:
    'Cache-Control': 'max-age=86400, private'
    'Content-Type': 'application/json; charset=utf-8'
    'Strict-Transport-Security': 'REDACTED'
    'X-Content-Type-Options': 'REDACTED'
    'Access-Control-Allow-Origin': 'REDACTED'
    'Access-Control-Allow-Methods': 'REDACTED'
    'P3P': 'REDACTED'
    'x-ms-request-id': 'some code>'
    'x-ms-ests-server': 'REDACTED'
    'x-ms-srs': 'REDACTED'
    'Content-Security-Policy-Report-Only': 'REDACTED'
    'X-XSS-Protection': 'REDACTED'
    'Set-Cookie': 'REDACTED'
    'Date': 'Sat, 19 Jul 2025 06:27:23 GMT'
    'Content-Length': '1753'



[2025-07-19T06:27:25.057Z] Request URL: 'https://login.microsoftonline.com/some code>/oauth2/v2.0/token'
Request method: 'POST'
Request headers:
    'Accept': 'application/json'
    'x-client-sku': 'REDACTED'
    'x-client-ver': 'REDACTED'
    'x-client-os': 'REDACTED'
    'x-ms-lib-capability': 'REDACTED'
    'client-request-id': 'REDACTED'
    'x-client-current-telemetry': 'REDACTED'
    'x-client-last-telemetry': 'REDACTED'
    'User-Agent': 'azsdk-python-identity/1.23.1 Python/3.11.5 (Windows-10-10.0.26100-SP0)'
A body is sent with the request
[2025-07-19T06:27:25.218Z] Response status: 200
Response headers:
    'Cache-Control': 'no-store, no-cache'
    'Pragma': 'no-cache'
    'Content-Type': 'application/json; charset=utf-8'
    'Expires': '-1'
    'Strict-Transport-Security': 'REDACTED'
    'X-Content-Type-Options': 'REDACTED'
    'P3P': 'REDACTED'
    'client-request-id': 'REDACTED'
    'x-ms-request-id': 'some code>'
    'x-ms-ests-server': 'REDACTED'
    'x-ms-clitelem': 'REDACTED'
    'x-ms-srs': 'REDACTED'
    'Content-Security-Policy-Report-Only': 'REDACTED'
    'X-XSS-Protection': 'REDACTED'
    'Set-Cookie': 'REDACTED'
    'Date': 'Sat, 19 Jul 2025 06:27:24 GMT'
    'Content-Length': '1627'



[2025-07-19T06:27:25.225Z] DefaultAzureCredential acquired a token from EnvironmentCredential
[2025-07-19T06:27:25.229Z] Request URL: 'https://None.blob.core.windows.net/None-bronze?restype=REDACTED&comp=REDACTED'
Request method: 'GET'
Request headers:
    'x-ms-version': 'REDACTED'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.26.0 Python/3.11.5 (Windows-10-10.0.26100-SP0)'
    'x-ms-date': 'REDACTED'
    'x-ms-client-request-id': 'some code>'
    'Authorization': 'REDACTED'
No body was attached to the request
[2025-07-19T06:27:25.872Z] Response status: 401
Response headers:
    'Content-Length': '402'
    'Content-Type': 'application/xml'
    'Server': 'Microsoft-HTTPAPI/2.0'
    'x-ms-request-id': 'some code>'
    'x-ms-error-code': 'InvalidAuthenticationInfo'
    'WWW-Authenticate': 'Bearer authorization_uri=https://login.microsoftonline.com/some code>/oauth2/authorize resource_id=https://storage.azure.com'
    'Date': 'Sat, 19 Jul 2025 06:27:24 GMT'



[2025-07-19T06:27:25.875Z] ClientSecretCredential.get_token_info failed: The current credential is not configured to acquire tokens for tenant <some code>. To enable acquiring tokens for this tenant add it to the additionally_allowed_tenants when creating the credential, or add "*" to additionally_allowed_tenants to allow acquiring tokens for any tenant.
[2025-07-19T06:27:25.877Z] EnvironmentCredential.get_token_info failed: The current credential is not configured to acquire tokens for tenant <some code>. To enable acquiring tokens for this tenant add it to the additionally_allowed_tenants when creating the credential, or add "*" to additionally_allowed_tenants to allow acquiring tokens for any tenant.
[2025-07-19T06:27:27.905Z] Host lock lease acquired by instance ID '0000000000000000000000009599A384'.
[2025-07-19T06:27:44.645Z] ClientSecretCredential.get_token_info succeeded
[2025-07-19T06:27:44.652Z] EnvironmentCredential.get_token_info succeeded
[2025-07-19T06:27:44.655Z] DefaultAzureCredential acquired a token from EnvironmentCredential
[2025-07-19T06:27:44.657Z] Request URL: 'https://None.blob.core.windows.net/None-bronze?restype=REDACTED&comp=REDACTED'
Request method: 'GET'
Request headers:
    'x-ms-version': 'REDACTED'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.26.0 Python/3.11.5 (Windows-10-10.0.26100-SP0)'
    'x-ms-date': 'REDACTED'
    'x-ms-client-request-id': '<some code>'
    'Authorization': 'REDACTED'
No body was attached to the request
[2025-07-19T06:27:44.793Z] Response status: 401
Response headers:
    'Content-Length': '402'
    'Content-Type': 'application/xml'
    'Server': 'Microsoft-HTTPAPI/2.0'
    'x-ms-request-id': '<some code>'
    'x-ms-error-code': 'InvalidAuthenticationInfo'
    'WWW-Authenticate': 'Bearer authorization_uri=https://login.microsoftonline.com/<some code>/oauth2/authorize resource_id=https://storage.azure.com'
    'Date': 'Sat, 19 Jul 2025 06:27:43 GMT'
[2025-07-19T06:27:44.797Z] ClientSecretCredential.get_token_info failed: The current credential is not configured to acquire tokens for tenant <some code>. To enable acquiring tokens for this tenant add it to the additionally_allowed_tenants when creating the credential, or add "*" to additionally_allowed_tenants to allow acquiring tokens for any tenant.
[2025-07-19T06:27:44.799Z] EnvironmentCredential.get_token_info failed: The current credential is not configured to acquire tokens for tenant <some code>. To enable acquiring tokens for this tenant add it to the additionally_allowed_tenants when creating the credential, or add "*" to additionally_allowed_tenants to allow acquiring tokens for any tenant.
[2025-07-19T06:28:11.057Z] ClientSecretCredential.get_token_info succeeded
[2025-07-19T06:28:11.065Z] EnvironmentCredential.get_token_info succeeded
[2025-07-19T06:28:11.068Z] DefaultAzureCredential acquired a token from EnvironmentCredential
[2025-07-19T06:28:11.071Z] Request URL: 'https://None.blob.core.windows.net/None-bronze?restype=REDACTED&comp=REDACTED'
Request method: 'GET'
Request headers:
    'x-ms-version': 'REDACTED'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.26.0 Python/3.11.5 (Windows-10-10.0.26100-SP0)'
    'x-ms-date': 'REDACTED'
    'x-ms-client-request-id': '<some code>'
    'Authorization': 'REDACTED'
No body was attached to the request
[2025-07-19T06:28:11.202Z] Response status: 401
Response headers:
    'Content-Length': '402'
    'Content-Type': 'application/xml'
    'Server': 'Microsoft-HTTPAPI/2.0'
    'x-ms-request-id': '<some code>'
    'x-ms-error-code': 'InvalidAuthenticationInfo'
    'WWW-Authenticate': 'Bearer authorization_uri=https://login.microsoftonline.com/d66b82bb-f065-4aec-8010-59d40b30df02/oauth2/authorize resource_id=https://storage.azure.com'
    'Date': 'Sat, 19 Jul 2025 06:28:09 GMT'
[2025-07-19T06:28:11.206Z] ClientSecretCredential.get_token_info failed: The current credential is not configured to acquire tokens for tenant <some code>. To enable acquiring tokens for this tenant add it to the additionally_allowed_tenants when creating the credential, or add "*" to additionally_allowed_tenants to allow acquiring tokens for any tenant.
[2025-07-19T06:28:11.209Z] EnvironmentCredential.get_token_info failed: The current credential is not configured to acquire tokens for tenant <some code>. To enable acquiring tokens for this tenant add it to the additionally_allowed_tenants when creating the credential, or add "*" to additionally_allowed_tenants to allow acquiring tokens for any tenant.
[2025-07-19T06:28:53.346Z] ClientSecretCredential.get_token_info succeeded
[2025-07-19T06:28:53.349Z] EnvironmentCredential.get_token_info succeeded
[2025-07-19T06:28:53.351Z] DefaultAzureCredential acquired a token from EnvironmentCredential
[2025-07-19T06:28:53.354Z] Request URL: 'https://None.blob.core.windows.net/None-bronze?restype=REDACTED&comp=REDACTED'
Request method: 'GET'
Request headers:
    'x-ms-version': 'REDACTED'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.26.0 Python/3.11.5 (Windows-10-10.0.26100-SP0)'
    'x-ms-date': 'REDACTED'
    'x-ms-client-request-id': '<some code>'
    'Authorization': 'REDACTED'
No body was attached to the request
[2025-07-19T06:28:53.491Z] Response status: 401
Response headers:
    'Content-Length': '402'
    'Content-Type': 'application/xml'
    'Server': 'Microsoft-HTTPAPI/2.0'
    'x-ms-request-id': '<some code>'
    'x-ms-error-code': 'InvalidAuthenticationInfo'
    'WWW-Authenticate': 'Bearer authorization_uri=https://login.microsoftonline.com/d66b82bb-f065-4aec-8010-59d40b30df02/oauth2/authorize resource_id=https://storage.azure.com'
    'Date': 'Sat, 19 Jul 2025 06:28:52 GMT'
```

* `Access-Control-Max-Age` is a response header that specifies how long the results of a preflight request can be cached by the browser

* ok so I tried to add the allowed origins for the azure blob storage account under the settings > CORS tab where blob service, allowed origins, allowed methods, allowed headers, exposed headers and max age where set to *, [GET, POST, PUT, DELETE, HEAD, MERGE, OPTIONS, PATCH], [x-ms-blob-type, content-type], <blank>, and 0 respectively. But to no avail talagang response 403 pa rin. AuthorizationPermissionMismatch I think is really something to do with my service principal or the roles it has been assigned to. Kasi wala pa rin eh

that is when I tested the storage access key itself which microsoft says is one of the authenticationmethods you can use when dealing with storage accounts apart from microsoft entra id, shared access signatures, 
```
* >>>
>>> from azure.storage.blob import BlobServiceClient
>>>
>>>
>>> conn_str = "DefaultEndpointsProtocol=https;AccountName=sgppipelinesa;AccountKey=<acc key>;EndpointSuffix=core.windows.net"
>>> conn_key = "<acc key>"
>>>
>>> blob_service_client = BlobServiceClient.from_connection_string(connection_string)
>>> blob_service_client = BlobServiceClient.from_connection_string(conn_str)
>>> containers = blob_service_client.list_containers()
>>>
>>> for container in containers:
...     print(container.name)
...
sgppipelinesa-bronze
sgppipelinesa-gold
sgppipelinesa-silver
>>> bronze_container = blob_service_client.get_container_client(container=f"sgppipelinesa-bronze")
>>> files = bronze_container.list_blobs()
>>> [file for file in files]
[{'name': '1028-20100710-hne/LICENSE', 'container': 'sgppipelinesa-bronze', ..., 'has_versions_only': None}]
```

* the listing of blob containers finally worked when I used ClientSecretCredentials class, isntead of DefaultAzureCredentials. Fail because yes listing of blob containers works but listing the files inside the blob containers still doesn't work no matter what credential type you use or no matter if you still assign a role for the microsoft entra id you have at the level of the container itself
```
Request URL: 'https://login.microsoftonline.com/<some code>/v2.0/.well-known/openid-configuration'
Request method: 'GET'
Request headers:
    'User-Agent': 'azsdk-python-identity/1.23.1 Python/3.11.5 (Windows-10-10.0.26100-SP0)'
No body was attached to the request
[2025-07-19T08:12:00.067Z] Response status: 200
Response headers:
    'Cache-Control': 'max-age=86400, private'
    'Content-Type': 'application/json; charset=utf-8'
    'Strict-Transport-Security': 'REDACTED'
    'X-Content-Type-Options': 'REDACTED'
    'Access-Control-Allow-Origin': 'REDACTED'
    'Access-Control-Allow-Methods': 'REDACTED'
    'P3P': 'REDACTED'
    'x-ms-request-id': '<some code>'
    'x-ms-ests-server': 'REDACTED'
    'x-ms-srs': 'REDACTED'
    'Content-Security-Policy-Report-Only': 'REDACTED'
    'X-XSS-Protection': 'REDACTED'
    'Set-Cookie': 'REDACTED'
    'Date': 'Sat, 19 Jul 2025 08:11:59 GMT'
    'Content-Length': '1753'
[2025-07-19T08:12:00.080Z] Request URL: 'https://login.microsoftonline.com/<some code>/oauth2/v2.0/token'
Request method: 'POST'
Request headers:
    'Accept': 'application/json'
    'x-client-sku': 'REDACTED'
    'x-client-ver': 'REDACTED'
    'x-client-os': 'REDACTED'
    'x-ms-lib-capability': 'REDACTED'
    'client-request-id': 'REDACTED'
    'x-client-current-telemetry': 'REDACTED'
    'x-client-last-telemetry': 'REDACTED'
    'User-Agent': 'azsdk-python-identity/1.23.1 Python/3.11.5 (Windows-10-10.0.26100-SP0)'
A body is sent with the request
[2025-07-19T08:12:00.212Z] Response status: 200
Response headers:
    'Cache-Control': 'no-store, no-cache'
    'Pragma': 'no-cache'
    'Content-Type': 'application/json; charset=utf-8'
    'Expires': '-1'
    'Strict-Transport-Security': 'REDACTED'
    'X-Content-Type-Options': 'REDACTED'
    'P3P': 'REDACTED'
    'client-request-id': 'REDACTED'
    'x-ms-request-id': '<some code>'
    'x-ms-ests-server': 'REDACTED'
    'x-ms-clitelem': 'REDACTED'
    'x-ms-srs': 'REDACTED'
    'Content-Security-Policy-Report-Only': 'REDACTED'
    'X-XSS-Protection': 'REDACTED'
    'Set-Cookie': 'REDACTED'
    'Date': 'Sat, 19 Jul 2025 08:11:59 GMT'
    'Content-Length': '1628'
[2025-07-19T08:12:00.217Z] ClientSecretCredential.get_token_info succeeded
[2025-07-19T08:12:00.219Z] Request URL: 'https://testingforentraid.blob.core.windows.net/?comp=REDACTED&include=REDACTED'
Request method: 'GET'
Request headers:
    'x-ms-version': 'REDACTED'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.26.0 Python/3.11.5 (Windows-10-10.0.26100-SP0)'
    'x-ms-date': 'REDACTED'
    'x-ms-client-request-id': '<some code>'
    'Authorization': 'REDACTED'
No body was attached to the request
[2025-07-19T08:12:01.804Z] Response status: 200
Response headers:
    'Transfer-Encoding': 'chunked'
    'Content-Type': 'application/xml'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-request-id': '<some code>'
    'x-ms-client-request-id': '<some code>'
    'x-ms-version': 'REDACTED'
    'Date': 'Sat, 19 Jul 2025 08:12:00 GMT'
[2025-07-19T08:12:01.806Z] {'name': 'test', 'last_modified': datetime.datetime(2025, 7, 19, 8, 5, 9, tzinfo=datetime.timezone.utc), 'etag': '"0x8DDC69AFB3E36F9"', 'lease': {'status': 'unlocked', 'state': 'available', 'duration': None}, 'public_access': None, 'has_immutability_policy': False, 'deleted': None, 'version': None, 'has_legal_hold': False, 'metadata': None, 'encryption_scope': <azure.storage.blob._models.ContainerEncryptionScope object at 0x0000023E7FCD6F90>, 'immutable_storage_with_versioning_enabled': False}
``` 

I also found out that even though storage access key is disabled, that when I try to list blob files that it still gets a 403 error. I tested this with the original storage account containing the gold, silver, bronze containers, and it managed to lsit it all but the files no.

* 
```
>>>
>>> import time
>>> import os
>>> import azure.functions as func
>>> import logging
>>>
>>> from azure.identity import DefaultAzureCredential, ClientSecretCredential
>>> from azure.storage.blob import BlobServiceClient
>>> from azure.storage.filedatalake import DataLakeServiceClient, DataLakeDirectoryClient
>>>
>>> from dotenv import load_dotenv
>>> from pathlib import Path
>>>
>>> env_dir = Path('../').resolve()
>>> load_dotenv(os.path.join(env_dir, '.env'))
True
>>> # Retrieve credentials from environment variables
>>> tenant_id = os.environ.get("AZURE_TENANT_ID")
>>> client_id = os.environ.get("AZURE_CLIENT_ID")
>>> client_secret = os.environ.get("AZURE_CLIENT_SECRET")
>>> storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
>>>
>>> credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
>>> # credential = DefaultAzureCredential()
>>>
>>> # Create a BlobServiceClient object
>>> blob_service_client = BlobServiceClient(
...     account_url=f"https://{storage_account_name}.blob.core.windows.net",
...     credential=credential,
... )
>>>
>>> container_client = blob_service_client.get_container_client(container=f"{storage_account_name}-bronze")
>>> container_client
<azure.storage.blob._container_client.ContainerClient object at 0x000001C85F6B5F50>
>>> container_client.account_name
'sgppipelinesa'
>>>
>>> container_client.list_blobs()
<iterator object azure.core.paging.ItemPaged at 0x1c85f6b6c50>
>>> for file in container_client.list_blobs():
...     print(file)
...
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "c:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc\.venv\Lib\site-packages\azure\core\paging.py", line 136, in __next__
    return next(self._page_iterator)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "c:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc\.venv\Lib\site-packages\azure\core\paging.py", line 82, in __next__
    self._response = self._get_next(self.continuation_token)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "c:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc\.venv\Lib\site-packages\azure\storage\blob\_list_blobs_helper.py", line 96, in _get_next_cb
    process_storage_error(error)
  File "c:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc\.venv\Lib\site-packages\azure\storage\blob\_shared\response_handlers.py", line 190, in process_storage_error
    exec("raise error from None")  # pylint: disable=exec-used # nosec
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1, in <module>
azure.core.exceptions.HttpResponseError: This request is not authorized to perform this operation using this permission.
RequestId:<some code>
Time:2025-07-19T08:53:03.8592111Z
ErrorCode:AuthorizationPermissionMismatch
Content: <?xml version="1.0" encoding="utf-8"?><Error><Code>AuthorizationPermissionMismatch</Code><Message>This request is not authorized to perform this operation using this permission.
RequestId:<some code>
Time:2025-07-19T08:53:03.8592111Z</Message></Error>
>>>
>>> with open(file="../include/data/1028-20100710-hne.tgz", mode="rb") as data:
...     blob_client = container_client.upload_blob(name="sample-blob.tgz", data=data, overwrite=True)
...
Traceback (most recent call last):
  File "<stdin>", line 2, in <module>
  File "c:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc\.venv\Lib\site-packages\azure\core\tracing\decorator.py", line 119, in wrapper_use_tracer
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "c:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc\.venv\Lib\site-packages\azure\storage\blob\_container_client.py", line 1104, in upload_blob
    blob.upload_blob(
  File "c:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc\.venv\Lib\site-packages\azure\core\tracing\decorator.py", line 119, in wrapper_use_tracer
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "c:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc\.venv\Lib\site-packages\azure\storage\blob\_blob_client.py", line 615, in upload_blob
    return upload_block_blob(**options)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "c:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc\.venv\Lib\site-packages\azure\storage\blob\_upload_helpers.py", line 197, in upload_block_blob
    process_storage_error(error)
  File "c:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc\.venv\Lib\site-packages\azure\storage\blob\_shared\response_handlers.py", line 190, in process_storage_error
    exec("raise error from None")  # pylint: disable=exec-used # nosec
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1, in <module>
azure.core.exceptions.HttpResponseError: This request is not authorized to perform this operation using this permission.
RequestId:<some code>
Time:2025-07-19T08:58:32.6891244Z
ErrorCode:AuthorizationPermissionMismatch
Content: <?xml version="1.0" encoding="utf-8"?><Error><Code>AuthorizationPermissionMismatch</Code><Message>This request is not authorized to perform this operation using this permission.
RequestId:<some code>
Time:2025-07-19T08:58:32.6891244Z</Message></Error>

>>> container_client.get_container_access_policy()
{'public_access': None, 'signed_identifiers': []}
```

this `{'public_access': None, 'signed_identifiers': []}` maybe a sign that we do not have access to writing stuff inside the container

* the reason why the unit access catalog connector does not show in the resource group where the azure databricks you crreated belongs to is because when terraform created it the sku or stock keeping units was set to standard, but if we created this in azure portal and selected the pricing tier which is the sku in terraform to be in premium. We only set our sku to be standard and as a result we don't see the unit access catalog connector

# Articles, Videos, Papers: 
* terraform tutorial for setting up azure services via code: https://developer.hashicorp.com/terraform/tutorials/azure-get-started/infrastructure-as-code
* end to end azure DE tutorial: https://www.youtube.com/watch?v=lyp8rlpJc3k&list=PLCBT00GZN_SAzwTS-SuLRM547_4MUHPuM&index=45&t=5222s
* after watching tutorial this is for magnifying your understanding to a typical DE project: https://www.youtube.com/watch?v=T8ahyYdSCGg

* integrating azure key vault with azure functions so that we can write to and from the azure data lake with our azure credentials: https://medium.com/@dssc2022yt/accessing-azure-key-vault-secrets-with-azure-functions-2e651980f292
* authorizationpermissionmismatch: https://learn.microsoft.com/en-us/answers/questions/1657784/authorizationpermissionmismatch-error-when-accessi
https://learn.microsoft.com/en-us/rest/api/storageservices/get-user-delegation-key#authorization
https://learn.microsoft.com/en-us/answers/questions/959836/authorizationpermissionmismatch-while-performing-o

closest one to my problem:
https://stackoverflow.com/questions/78351027/getting-errorcodeauthorizationpermissionmismatch-when-listing-blobs-from-python
https://stackoverflow.com/questions/78529445/azure-container-access-via-python-sdk-fails-with-authorizationpermissionmismatch

* setting azure data lake storage CORS programmatically: https://stackoverflow.com/questions/28894466/how-can-i-set-cors-in-azure-blob-storage-in-portal