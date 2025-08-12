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

* coy the `subscription id` we listed earlier via `az account list` or from the `az login` command and now run `az ad sp create-for-rbac --role="Contributor" --scopes="/subscriptions/<SUBSCRIPTION_ID>"` which creates the equivalent of an IAM user in AWS which will output certain credentials we need to keep safe as this will be keys needed to access our azure services like azure data lake storage 

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

* the most likely reason why you are still encoutnering a code 500 internal server error even when you've added `*`, `https://portal.azure.com`, `https://functions.azure.com`, `https://*.com`, and `http://*.com` to solve the cross origin resource sharing error is because you maybe using a relative module inside your `function_app.py` that has not been included in deployment. https://stackoverflow.com/questions/68009769/azure-function-500-internal-internal-server-error-in-run-test-mode


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
* 
from azure.storage.blob import BlobServiceClient


conn_str = "DefaultEndpointsProtocol=https;AccountName=sgppipelinesa;AccountKey=<acc key>;EndpointSuffix=core.windows.net"
conn_key = "<acc key>"

blob_service_client = BlobServiceClient.from_connection_string(connection_string)
blob_service_client = BlobServiceClient.from_connection_string(conn_str)
containers = blob_service_client.list_containers()

for container in containers:
    print(container.name)

sgppipelinesa-bronze
sgppipelinesa-gold
sgppipelinesa-silver
bronze_container = blob_service_client.get_container_client(container=f"sgppipelinesa-bronze")
files = bronze_container.list_blobs()
[file for file in files]
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

the idea is this, users, groups, and service principals that use client id, tenant id, client secret keys are under the microsoft entra id a cloud based identity and access management services formerly azure active directory

we can also use shared access keys/storage account access keys in a storage account which we can retrieve if we did enable storage account access keys, which are actually less secure and azure actually advises that we don't use these keys

another is shared access keys which is a fine grained version of storage account access keys which have more specific permissions/roles that we can assign to whoever has this key e.g. a shared access key that can read write update a storage blob container

these are just ways to authenticate to a storage account or any kind of service/resource that uses authentication, and overall these are under the service, user, and groups category of kinds of identities under the user type which is different from managed identities which are akin to AWS IAM users which are assigned keys and where these users

Managed identities for Azure resources are service principals that create a Microsoft Entra identity and specific permissions for Azure managed resources. **Managed identities are a safer way to grant access to storage data and replace the requirement for you to include shared access signature tokens (SAS)** with your source and target container URLs.

creating managed identities with azure functions to integrate with azure blob storage or azure data lake storage2 

* using shared access keys can be an alternatvie because how it works is we basically use a url instead to read and write to a azure blob container which we actually cna create if we go to our container > shared access keys > specify permissions (read, write, list, update, delete, add, create)
```
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.storage.blob import BlobServiceClient
import requests
from datetime import datetime, timedelta
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from pathlib import Path

import os

env_dir = Path('./').resolve()
load_dotenv(os.path.join(env_dir, '.env'))

# Retrieve credentials from environment variables
tenant_id = os.environ.get("AZURE_TENANT_ID")
client_id = os.environ.get("AZURE_CLIENT_ID")
client_secret = os.environ.get("AZURE_CLIENT_SECRET")
subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
resource_group_name = os.environ.get("RESOURCE_GROUP_NAME")

credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)

# Create a BlobServiceClient object
blob_service_client = BlobServiceClient(account_url=f"https://{storage_account_name}.blob.core.windows.net", credential=credential,)
token = credential.get_token("https://management.azure.com/.default").token


# url + token: https://<storage account name>.blob.core.windows.net/<storage account container>?sp=racwdl&st=2025-07-22T09:15:41Z&se=2025-07-22T17:30:41Z&skoid=<signed object id that's created>&sktid=2e048c9e-b551-4c29-9888-80fb187ca009&skt=2025-07-22T09:15:41Z&ske=2025-07-22T17:30:41Z&sks=b&skv=2024-11-04&spr=https&sv=2024-11-04&sr=c&sig=HjHl7b8%2F%2FPeB%2F7URHBwTemxIqVoU4Od%2FiWf4uCge0zU%3D
# sp=racwdl&st=2025-07-22T09:15:41Z&se=2025-07-22T17:30:41Z&skoid=d092f89d-60e5-43d7-8a6e-d353f83f69d5&sktid=2e048c9e-b551-4c29-9888-80fb187ca009&skt=2025-07-22T09:15:41Z&ske=2025-07-22T17:30:41Z&sks=b&skv=2024-11-04&spr=https&sv=2024-11-04&sr=c&sig=HjHl7b8%2F%2FPeB%2F7URHBwTemxIqVoU4Od%2FiWf4uCge0zU%3D
url = "https://<storage account name>.blob.core.windows.net/<storage account container>"
body = {
    # signed permissions (required)
    "sp": "racwdl",

    # signed start indicate the start and expiration times for 
    # shared access key
    "st": "2025-07-22T09:15:41Z",
    "se": "2025-07-22T17:30:41Z",

    # object id (required) The Get User Delegation Key 
    # operation returns this value as part of the response
    # which is another rqeuest in of itself
    "skoid": "d092f89d-60e5-43d7-8a6e-d353f83f69d5",

    # tenant id (required) The Get User Delegation Key 
    # operation returns this value as part of the response
    # which is another rqeuest in of itself
    "sktid": "2e048c9e-b551-4c29-9888-80fb187ca009",

    # signed key start time (required) start of the lifetime 
    # of the user delegation key in ISO Date format. The Get 
    # User Delegation Key operation returns this value as 
    # part of the response.
    "skt": "2025-07-22T09:15:41Z",

    # signed key expiry time (required) end of the lifetime 
    # of the user delegation key in ISO Date format. The Get 
    # User Delegation Key operation returns this value as 
    # part of the response.
    "ske": "2025-07-22T17:30:41Z",

    # signed authorized object id (optional)
    "sks": "b",

    # signed key version (required) The value is returned 
    # by the Get User Delegation Key operation. Specifies
    # the storage service version that was used to get 
    # the user delegation key
    "skv": "2024-11-04",

    # signed protocol (optional) can be values like "https" or
    # ("https", "http")
    "spr": "https",

    # signed version,
    "sv": "2024-11-04", 

    # signed resource (required) b and c mean we want 
    # access to blobs (files) and containers as well 
    # as the blobs within the containers 
    "sr": "c",

    # signature (required)
    "sig": "HjHl7b8%2F%2FPeB%2F7URHBwTemxIqVoU4Od%2FiWf4uCge0zU%3D"
}
response = requests.post(url, headers=f"Authorization: Bearer {token}", json=body)
response.json()["serviceSasToken"]
```

this is for a user delegated shared access signature. Motherfucker was simpole enough until another 403 error

but ff. is for account shared access signature
```
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.storage.blob import BlobServiceClient
import requests
from datetime import datetime, timedelta
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from pathlib import Path
import os

env_dir = Path('./').resolve()
load_dotenv(os.path.join(env_dir, '.env'))
 
# Retrieve credentials from environment variables
tenant_id = os.environ.get("AZURE_TENANT_ID")
client_id = os.environ.get("AZURE_CLIENT_ID")
client_secret = os.environ.get("AZURE_CLIENT_SECRET")
subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
resource_group_name = os.environ.get("RESOURCE_GROUP_NAME")

credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)

# Create a BlobServiceClient object
blob_service_client = BlobServiceClient(account_url=f"https://{storage_account_name}.blob.core.windows.net", credential=credential,)
token = credential.get_token("https://management.azure.com/.default").token

sas_url = (
    f"https://management.azure.com/subscriptions/{subscription_id}/"
    f"resourceGroups/{resource_group_name}/providers/Microsoft.Storage/"
    f"storageAccounts/{storage_account_name}/listServiceSas/?api-version=2021-09-01"
)

signed_exp = (datetime.utcnow() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
body = {"signedVersion": "2025-01-01", "canonicalizedResource": f"/blob/{storage_account_name}/{storage_account_name}-bronze", "signedResourceTypes": "c", "signedPermissions": "l", "signedProtocol": "https", "signedExpiry": signed_exp}

response = requests.post(sas_url, headers={"Authorization": f"Bearer {token}"}, json=body)

sas_token = response.json()['serviceSasToken']
blob_service_client = BlobServiceClient(account_url=f"https://{storage_account_name}.blob.core.windows.net", credential=sas_token)
container_client = blob_service_client.get_container_client("{storage_account_name}-bronze")

for file in container_client.list_blobs():
...     print(file.name)
```

SignedServices (ss)	Required. Specifies the signed services that are accessible with the account SAS. Possible values include:

- Blob (b)
- Queue (q)
- Table (t)
- File (f)

You can combine values to provide access to more than one service. For example, ss=bf specifies access to the Blob Storage and Azure Files endpoints. E.g. `{"signedServices": "bfqt", ...}` where `b` is for blob, `f` is for file, `q` is for queue, and `t` is for table

gets ko na
if you want to list containers you would generate shared access signature at the level of the storage account, specify `s` as the `signedResourceTypes` e.g. `{"signedResourceTypes": "s", ...}`, and then specify `l` as the `signedPermissions`

note you can combine values to provide access to more than one resource type. For example, `{"signedResourceTypes": "sco", ...}` which accesses service itself, containers, and objects

if you want to list blobs and files inside the container you would generate shared access signature at the level of the storage account, and then specify `c`, and `o` as the `signedResourceTypes` which gets container properties, metadata, sets container metadata, deletes containers, gets, sets, creates, adds, lists, updates, deletes, processes, immutable storage, perm delete objects in the container

full list:
```
Operation	Signed service | Signed resource type | Signed permission
List Containers | Blob (b) | Service (s) | List (l)
Get Blob Service Properties | Blob (b) | Service (s) | Read (r)
Set Blob Service Properties | Blob (b) | Service (s) | Write (w)
Get Blob Service Stats | Blob (b) | Service (s) | Read (r)
Create Container | Blob (b) | Container (c) | Create(c) or Write (w)
Get Container Properties | Blob (b) | Container (c) | Read (r)
Get Container Metadata | Blob (b) | Container (c) | Read (r)
Set Container Metadata | Blob (b) | Container (c) | Write (w)
Lease Container | Blob (b) | Container (c) | Write (w) or Delete (d)1
Delete Container | Blob (b) | Container (c) | Delete (d)1
Find Blobs by Tags in Container | Blob (b) | Container (c) | Filter (f)
List Blobs | Blob (b) | Container (c) | List (l)
Put Blob (create new block blob) | Blob (b) | Object (o) | Create (c) or Write (w)
Put Blob (overwrite existing block blob) | Blob (b) | Object (o) | Write (w)
Put Blob (create new page blob) | Blob (b) | Object (o) | Create (c) or Write (w)
Put Blob (overwrite existing page blob) | Blob (b) | Object (o) | Write (w)
Get Blob | Blob (b) | Object (o) | Read (r)
Get Blob Properties | Blob (b) | Object (o) | Read (r)
Set Blob Properties | Blob (b) | Object (o) | Write (w)
Get Blob Metadata | Blob (b) | Object (o) | Read (r)
Set Blob Metadata | Blob (b) | Object (o) | Write (w)
Get Blob Tags | Blob (b) | Object (o) | Tags (t)
Set Blob Tags | Blob (b) | Object (o) | Tags (t)
Find Blobs by Tags | Blob (b) | Object (o) | Filter (f)
Delete Blob | Blob (b) | Object (o) | Delete (d)1
Delete Blob Version | Blob (b) | Object (o) | Delete Version (x)2
Permanently Delete Snapshot / Version | Blob (b) | Object (o) | Permanent Delete (y)3
Lease Blob | Blob (b) | Object (o) | Write (w) or Delete (d)1
Snapshot Blob | Blob (b) | Object (o) | Create (c) or Write (w)
Copy Blob (destination is new blob) | Blob (b) | Object (o) | Create (c) or Write (w)
Copy Blob (destination is an existing blob) | Blob (b) | Object (o) | Write (w)
Incremental Copy | Blob (b) | Object (o) | Create (c) or Write (w)
Abort Copy Blob | Blob (b) | Object (o) | Write (w)
Put Block | Blob (b) | Object (o) | Write (w)
Put Block List (create new blob) | Blob (b) | Object (o) | Write (w)
Put Block List (update existing blob) | Blob (b) | Object (o) | Write (w)
Get Block List | Blob (b) | Object (o) | Read (r)
Put Page | Blob (b) | Object (o) | Write (w)
Get Page Ranges | Blob (b) | Object (o) | Read (r)
Append Block | Blob (b) | Object (o) | Add (a) or Write (w)
Clear Page | Blob (b) | Object (o) | Write (w)
```


```
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.storage.blob import BlobServiceClient
import requests
from datetime import datetime, timedelta
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from pathlib import Path
import os

env_dir = Path('./').resolve()
load_dotenv(os.path.join(env_dir, '.env'))
True

# Retrieve credentials from environment variables
tenant_id = os.environ.get("AZURE_TENANT_ID")
client_id = os.environ.get("AZURE_CLIENT_ID")
client_secret = os.environ.get("AZURE_CLIENT_SECRET")
subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
resource_group_name = os.environ.get("RESOURCE_GROUP_NAME")

credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)

# Create a BlobServiceClient object
blob_service_client = BlobServiceClient(account_url=f"https://{storage_account_name}.blob.core.windows.net", credential=credential,)
token = credential.get_token("https://management.azure.com/.default").token

sas_url = (
...     f"https://management.azure.com/subscriptions/{subscription_id}/"
...     f"resourceGroups/{resource_group_name}/providers/Microsoft.Storage/"
...     f"storageAccounts/{storage_account_name}/listServiceSas/?api-version=2021-09-01"
... )

signed_exp = (datetime.utcnow() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
body = {"signedVersion": "2025-01-01", "signedServices": "bfqt", "signedResourceTypes": "sco", "signedPermissions": "rwdlacu", "signedProtocol": "https", "signedExpiry": signed_exp}

response = requests.post(sas_url, headers={"Authorization": f"Bearer {token}"}, json=body)

# generated sas token is at the level of the storage account, permitting services like blobs, files, queues, and tables to be read, listed, retrieved, updated, deleted etc. where allowed resource types are service, container 
sas_token = response.json()['serviceSasToken']
blob_service_client = BlobServiceClient(account_url=f"https://{storage_account_name}.blob.core.windows.net", credential=sas_token)
blob_service_client.list_containers()(
<iterator object azure.core.paging.ItemPaged at 0x215f7ab5190>
for cont in blob_service_client.list_containers)
  File "<stdin>", line 1
    for cont in blob_service_client.list_containers()
                                                     ^
SyntaxError: expected ':'
for cont in blob_service_client.list_containers():
...     print(cont)
...
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "c:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc\.venv\Lib\site-packages\azure\core\paging.py", line 136, in __next__
    return next(self._page_iterator)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "c:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc\.venv\Lib\site-packages\azure\core\paging.py", line 82, in __next__
    self._response = self._get_next(self.continuation_token)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "c:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc\.venv\Lib\site-packages\azure\storage\blob\_models.py", line 544, in _get_next_cb
    process_storage_error(error)
  File "c:\Users\LARRY\Documents\Scripts\data-engineering-path\signal-gender-predictor\azfunc\.venv\Lib\site-packages\azure\storage\blob\_shared\response_handlers.py", line 190, in process_storage_error
    exec("raise error from None")  # pylint: disable=exec-used # nosec
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1, in <module>
azure.core.exceptions.HttpResponseError: This request is not authorized to perform this operation using this resource type.
RequestId:1b57d78a-101e-0044-60ff-fa03a3000000
Time:2025-07-22T11:54:00.2105291Z
ErrorCode:AuthorizationResourceTypeMismatch
extendederrordetail:SignedResourceTypes 's' is required to perform this operation.
Content: <?xml version="1.0" encoding="utf-8"?><Error><Code>AuthorizationResourceTypeMismatch</Code><Message>This request is not authorized to perform this operation using this resource type.
RequestId:1b57d78a-101e-0044-60ff-fa03a3000000
Time:2025-07-22T11:54:00.2105291Z</Message><ExtendedErrorDetail>SignedResourceTypes 's' is required to perform this operation.</ExtendedErrorDetail></Error>
container_client = blob_service_client.get_container_client("sgppipelinesa-bronze")
container_client
<azure.storage.blob._container_client.ContainerClient object at 0x00000215F8B19890>
for blob in container_client.list_blobs():
...     print(blob)
```

useful resources: 
- https://learn.microsoft.com/en-us/azure/ai-services/translator/document-translation/how-to-guides/create-sas-tokens?tabs=Containers
account delegated shared access signature token: 
- https://learn.microsoft.com/en-us/rest/api/storageservices/create-account-sas#specify-an-ip-address-or-ip-range
user delegated shared access signature token: 
- https://learn.microsoft.com/en-us/rest/api/storageservices/create-user-delegation-sas#construct-a-user-delegation-sas
- https://prashanth-kumar-ms.medium.com/azure-managed-identity-integration-with-storage-account-5bea9261a4d1
getting user delegation key:  
- https://learn.microsoft.com/en-us/rest/api/storageservices/get-user-delegation-key
shared access signature did not match: 
- https://stackoverflow.com/questions/25038429/azure-shared-access-signature-signature-did-not-match
examples of creating account delegated shared access signature toeksn and using for blob storage operations:
- https://github.com/Azure-Samples/AzureStorageSnippets/blob/master/blobs/howto/python/blob-devguide-py/blob_devguide_create_sas.py

* the reason why the unit access catalog connector does not show in the resource group where the azure databricks you crreated belongs to is because when terraform created it the sku or stock keeping units was set to standard, but if we created this in azure portal and selected the pricing tier which is the sku in terraform to be in premium. We only set our sku to be standard and as a result we don't see the unit access catalog connector

* we when creating source/origin adn sink/datasets in azure data factory for copy activities the reason why we create parameters for these datasets is so that we can pass the items especially those used in a ForEach activity dynamically 

kumbaga ganto 
we define parameters `BaseURL` and `RelativeURL` at the level of our source/sink dataset
in our source dataset we set the value to be dynamic e.g. `@dataset().<param we define e.g. BaseURL or RelativeURL>`

going up once so that were now at the level of our, for example Copy activity which will be inside the ForEach activity we will see that the parameters we have defined will appear and we can then also set its value to be dynamic e.g. `item().<the key of the current item in the output of our Lookup activity which corresponds to a value e.g. BaseURL or RelativeURL>`

ff. are keys to remember when creating a `Copy` activity in ADF
- we need to define a source/origin dataset
- we need to define a sink/destination dataset
- we need to define a linked service that represents where the source/origin dataset will come from and what format it is
- we need to define a linked service that represents where the sink/destination dataset is to be dumped and what format it will be 


https://stackoverflow.com/questions/78080462/azure-data-factory-copy-data-http-source-zip-file-and-sink-as-azure-blob-storage


* what I dont understand yet is if azure key vault stores these credentials, won't we need some sort of permission again or credential again to access these credentials? For example my client secret is stored in key vault and I need a azure function to use it to authenticate programmatically to azure blob storage or azure data facory. Won't this require a credential to access a credential? And assuming we aren't in local development won't this credential need to be exposed some way in our azure function? Because of this azure key vault secrets public access? I'm confused eh.



You've hit upon a very important and common point of confusion when first learning about secure credential management in Azure! It seems like a chicken-and-egg problem: how do you get the first credential to get the other credentials?

The answer lies in Managed Identities for Azure Resources. This is the key to solving the "credential to access a credential" problem without exposing secrets.

Let's break it down:

The Problem: You're right, if your Azure Function needs a client secret from Key Vault, and Key Vault itself requires authentication (which it does), then how does the Function get the credential to authenticate to Key Vault? If you hardcode a credential in the Function's configuration to access Key Vault, you're back to square one with exposed secrets.

The Solution: Managed Identities

What they are: Managed Identities are a feature of Microsoft Entra ID (formerly Azure Active Directory) that provides Azure services (like Azure Functions, Azure Web Apps, Azure VMs, Azure Databricks) with an automatically managed identity in Microsoft Entra ID.

How they work:

When you enable a Managed Identity for your Azure Function App, Azure automatically creates a Service Principal (an identity for an application) in your Microsoft Entra ID tenant.

This Service Principal is automatically associated with your Azure Function App.

Crucially, Azure internally manages the lifecycle and credentials for this Managed Identity. You, as the developer, never see or handle these credentials.

You then grant this Managed Identity (your Function App's identity) permissions to access your Azure Key Vault. For example, you'd give it "Get" and "List" permissions on secrets in your Key Vault.

When your Azure Function code needs to retrieve a secret from Key Vault, it makes a request to Key Vault. Azure's underlying infrastructure automatically authenticates the Function using its Managed Identity, without any explicit credentials being provided by your code.

Once the Function has the client secret from Key Vault, it can then use that secret to authenticate to Azure Blob Storage, Azure Data Factory, or any other service that requires those credentials.

No Public Access / No Exposure:

You are correct that you don't want Key Vault secrets to have "public access." Key Vault secrets are private by default. Access is granted through Role-Based Access Control (RBAC) on the Key Vault itself.

Managed Identities solve the exposure problem because the "credential" used to access Key Vault is handled entirely by Azure's platform. Your Function code doesn't store it, doesn't retrieve it, and you don't see it. The connection is secure and internal to Azure.

In summary:

You do need a form of credential/permission to access Key Vault.

Managed Identities are that "credential."

The beauty is that Azure handles the management and security of this first "credential" (the Managed Identity's token) for you. You just enable it on your service and grant it permissions.

No exposure: Since you never see or manage the Managed Identity's underlying credential, there's no way for it to be accidentally exposed in your code, config files, or logs.

This is the recommended, secure pattern for Azure services to access other Azure resources that store secrets.

**medyo nagegets ko na how an azure function may indeed have access to a azure key vault secret key. It's because if we gave permission for this azure function or any kind of service like azure databricks for that matter using some kind of key, that these and only these apps can use this key to access the azure key vault credential**

```
what I dont understand yet is if azure key vault stores these credentials, won't we need some sort of permission again or credential again to access these credentials? For example my client secret is stored in key vault and I need a azure function to use it to authenticate programmatically to azure blob storage or azure data facory. Won't this require a credential to access a credential? And assuming we aren't in local development won't this credential need to be exposed some way in our azure function? Because of this azure key vault secrets public access? I'm confused eh.

You've hit upon a very important and common point of confusion when first learning about secure credential management in Azure! It seems like a chicken-and-egg problem: how do you get the first credential to get the other credentials?

The answer lies in Managed Identities for Azure Resources. This is the key to solving the "credential to access a credential" problem without exposing secrets.

Let's break it down:

The Problem: You're right, if your Azure Function needs a client secret from Key Vault, and Key Vault itself requires authentication (which it does), then how does the Function get the credential to authenticate to Key Vault? If you hardcode a credential in the Function's configuration to access Key Vault, you're back to square one with exposed secrets.

The Solution: Managed Identities

What they are: Managed Identities are a feature of Microsoft Entra ID (formerly Azure Active Directory) that provides Azure services (like Azure Functions, Azure Web Apps, Azure VMs, Azure Databricks) with an automatically managed identity in Microsoft Entra ID.

How they work:

When you enable a Managed Identity for your Azure Function App, Azure automatically creates a Service Principal (an identity for an application) in your Microsoft Entra ID tenant.

This Service Principal is automatically associated with your Azure Function App.

Crucially, Azure internally manages the lifecycle and credentials for this Managed Identity. You, as the developer, never see or handle these credentials.

You then grant this Managed Identity (your Function App's identity) permissions to access your Azure Key Vault. For example, you'd give it "Get" and "List" permissions on secrets in your Key Vault.

When your Azure Function code needs to retrieve a secret from Key Vault, it makes a request to Key Vault. Azure's underlying infrastructure automatically authenticates the Function using its Managed Identity, without any explicit credentials being provided by your code.

Once the Function has the client secret from Key Vault, it can then use that secret to authenticate to Azure Blob Storage, Azure Data Factory, or any other service that requires those credentials.

No Public Access / No Exposure:

You are correct that you don't want Key Vault secrets to have "public access." Key Vault secrets are private by default. Access is granted through Role-Based Access Control (RBAC) on the Key Vault itself.

Managed Identities solve the exposure problem because the "credential" used to access Key Vault is handled entirely by Azure's platform. Your Function code doesn't store it, doesn't retrieve it, and you don't see it. The connection is secure and internal to Azure.

In summary:

You do need a form of credential/permission to access Key Vault.

Managed Identities are that "credential."

The beauty is that Azure handles the management and security of this first "credential" (the Managed Identity's token) for you. You just enable it on your service and grant it permissions.

No exposure: Since you never see or manage the Managed Identity's underlying credential, there's no way for it to be accidentally exposed in your code, config files, or logs.

This is the recommended, secure pattern for Azure services to access other Azure resources that store secrets.

OHHH ok. So parang ganto ba: parang sa vercel app ba na pag ka dineploy mo na yung application and the application uses os.environ.get("SECRET_KEY") that this key is not necessarily a public key that anyone can use but the app and for the app itself is the only entity that can use this key?





Show thinking
Yes, your analogy with a Vercel app using os.environ.get("SECRET_KEY") is a good way to understand part of the concept, but let's refine it to highlight the unique security advantage of Azure Key Vault with Managed Identities.

Similarity to os.environ.get("SECRET_KEY") in a Vercel app:

Secrets out of Code: In both scenarios, the actual sensitive value (like your client secret) is not hardcoded directly into your application's source code (e.g., app.py). This is a fundamental security best practice.

Runtime Access: The application retrieves the secret at runtime. The environment variable, whether on Vercel or Azure, is securely injected into the application's runtime environment.

App-Specific Access: You are correct that this key is not "public." Only the deployed application instance has access to its configured environment variables. An external entity cannot just query Vercel or Azure and get your secret key from environment variables.

The Crucial Difference and Advantage of Azure Key Vault with Managed Identities:

Your confusion ("Won't this require a credential to access a credential?") is exactly what Managed Identities solve.

Think of it like this:

Your Vercel App (or Azure App Service without Managed Identity): You, the developer, manually input the SECRET_KEY into Vercel's environment variable configuration (or Azure's Application Settings). So, you are still the one handling the sensitive secret at some point (even if it's via a secure UI). The app then uses that SECRET_KEY because it's configured for it.

You provide the initial credential to the app's environment.

Your Azure Function with Azure Key Vault and Managed Identity:

You (the developer) store the sensitive client_secret directly into Azure Key Vault. This is the only place you put the raw secret.

You enable a Managed Identity for your Azure Function App. When you do this, Azure automatically creates a special identity for your Function in Microsoft Entra ID. You never see or handle any credential for this Managed Identity. It's managed by Azure itself.

You then grant Role-Based Access Control (RBAC) permissions on the Azure Key Vault. You explicitly tell Key Vault: "Allow this specific Managed Identity (your Function's identity) to Get secrets from me."

When your Function code runs and tries to retrieve a secret from Key Vault, Azure's platform automatically authenticates the Function using its Managed Identity. Your code doesn't need to provide any client ID, client secret, or certificate to Key Vault. It's all handled transparently by Azure.

Once the Function securely retrieves the client_secret from Key Vault (using its Managed Identity), it can then use that client_secret to authenticate to Azure Blob Storage, Azure Data Factory, or any other service.

In essence:

With Managed Identities, you eliminate the need to store or expose any secret to access your secrets. The "credential to access a credential" is handled by the underlying Azure platform, making the process much more secure.

Key Vault secrets do not have "public access." Access is strictly controlled via RBAC, typically granted to Managed Identities of other Azure services or specific Microsoft Entra ID users/groups.

so let's say na deploy na yung azure function ko and in this functions code I call on a class or another function from azure sdk that accesses the azure key vault secret e.g. client_secret = func_that_gets_azure_key_vault_client_secret(), can it be understood that if my azure function app has a manged identity for my function that this function once deployed can now and exclusively access this client secret from azure key vault?





Show thinking
Yes, you have understood it perfectly!

If your Azure Function App has a Managed Identity enabled, and you have granted that specific Managed Identity the necessary permissions (e.g., "Get" and "List" secrets) on your Azure Key Vault, then:

Once deployed, your Azure Function's code (e.g., client_secret = func_that_gets_azure_key_vault_client_secret()) will be able to programmatically and securely retrieve that client_secret from Key Vault.

And yes, in a practical and secure sense, it can now and exclusively access this client secret from Azure Key Vault, among the entities that you have authorized.

Let's break down the "exclusively" part:

Exclusively means: Only the identities (Managed Identities, users, service principals) that you have explicitly granted permission to on that specific secret in Key Vault can retrieve it. It's not publicly accessible, and other Azure Functions, VMs, or users in your subscription that haven't been granted access will be denied.

It does NOT mean: That you can't ever grant another entity access. If you later decide another Azure Function or a specific user also needs that secret, you would simply grant them permission in Key Vault as well.

This is the power of Managed Identities: you manage access at the Key Vault level by granting permissions to specific Azure resources, without ever embedding credentials for Key Vault itself into your code or configuration. Azure handles the initial authentication handshake for the Managed Identity transparently and securely.


Ok so in a tutorial it says that I should create an access policy in my azure key vault but I am unable to do so because it says access policies are not available. Some suggest its due to the permission model being set to "azure role-based access control" and not "vault access policy". My terraform infrastructure automatically set my azure key vault service to the following `resource "azurerm_key_vault" "kv" {

  name                        = "${var.project_name}kv"

  location                    = azurerm_resource_group.rg.location

  resource_group_name         = azurerm_resource_group.rg.name

  tenant_id                   = data.azurerm_client_config.current.tenant_id

  enabled_for_disk_encryption = true

  soft_delete_retention_days  = 7

  purge_protection_enabled    = false

  sku_name                    = "standard"



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



  enable_rbac_authorization = true

}` where enable_rbac_authorization was set to true. Could it be that why my azure key vault was created with permission model settings being set to "azure role based access control" is because of this configuration I didn't know my terraform infrastructure code had?



Show thinking
Yes, you are exactly right! Your diagnosis is spot on.

Your Terraform infrastructure code enable_rbac_authorization = true is precisely why your Azure Key Vault was created with the permission model set to "Azure role-based access control" instead of the older "Vault access policy" model.

Here's a breakdown:

Two Permission Models for Azure Key Vault:

Vault Access Policy (Legacy Model): This is the older, default model unless you specify otherwise. Permissions are managed directly within the Key Vault's "Access policies" blade in the Azure portal or via the access_policy block in Terraform. You assign granular permissions (Get, List, Set for secrets; Get, Sign for keys, etc.) to specific Microsoft Entra ID identities (users, groups, service principals, managed identities).

Azure Role-Based Access Control (RBAC) (Recommended Model): This is the newer, more granular, and recommended model. When this is enabled, Key Vault permissions are managed entirely through Azure's global RBAC system. Instead of creating "Access Policies" within the Key Vault resource itself, you assign built-in Azure roles (or custom roles) to identities at the Key Vault's scope (or even higher, like resource group or subscription).

enable_rbac_authorization = true in your Terraform:

This specific setting in your azurerm_key_vault resource tells Azure to use the Azure RBAC permission model for this Key Vault.

When enable_rbac_authorization is set to true, the access_policy block within your azurerm_key_vault resource is effectively ignored by Azure. Terraform might still accept it in the HCL (HashiCorp Configuration Language) and you'll see it in your state file, but Azure will not apply those access policies because you've chosen the RBAC model. This is why you see the message "Access policies are not available" in the portal.

What you need to do now:

Since your Key Vault is configured for Azure RBAC, you need to grant permissions using Azure Role Assignments, not the deprecated access policies.

For your Azure Function's Managed Identity to access secrets in this Key Vault, you would typically use a separate Terraform resource: azurerm_role_assignment.

Example of how to grant permissions via RBAC in Terraform:

Terraform

# Define your Key Vault
resource "azurerm_key_vault" "kv" {
  name                      = "${var.project_name}kv"
  location                  = azurerm_resource_group.rg.location
  resource_group_name       = azurerm_resource_group.rg.name
  tenant_id                 = data.azurerm_client_config.current.tenant_id
  # ... other Key Vault settings ...

  enable_rbac_authorization = true # This is the key setting
  
  # The 'access_policy' block here will be ignored because enable_rbac_authorization is true
  # access_policy {
  #   tenant_id = data.azurerm_client_config.current.tenant_id
  #   object_id = module.test_module.principal_id
  #   key_permissions = ["Get", "Create", "Update", "Import", "Delete"]
  #   secret_permissions = ["Get", "List", "Set", "Delete"]
  #   storage_permissions = ["Get"]
  # }
}

# Assuming you have an Azure Function App resource and its Managed Identity
# For example, if your Azure Function App is called 'my_function_app'
# You would first need to get its Managed Identity Principal ID
data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "rg" {
  name     = "${var.project_name}-rg"
  location = "East US"
}

resource "azurerm_function_app" "func_app" {
  name                = "${var.project_name}-func"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  app_service_plan_id = azurerm_app_service_plan.plan.id
  storage_account_name = azurerm_storage_account.sa.name
  storage_account_access_key = azurerm_storage_account.sa.primary_access_key
  # ... other function app settings ...

  identity {
    type = "SystemAssigned" # Enable a System-Assigned Managed Identity
  }
}

resource "azurerm_app_service_plan" "plan" {
  name                = "${var.project_name}-plan"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "FunctionApp"
  sku {
    tier = "Consumption"
    size = "Y1"
  }
}

resource "azurerm_storage_account" "sa" {
  name                     = "${var.project_name}sa"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}


# This is the correct way to grant permissions using RBAC
# Assign the "Key Vault Secrets User" role to your Function App's Managed Identity
resource "azurerm_role_assignment" "key_vault_secret_user_assignment" {
  scope                = azurerm_key_vault.kv.id
  role_definition_name = "Key Vault Secrets User" # Standard role for getting secrets
  principal_id         = azurerm_function_app.func_app.identity[0].principal_id # Use the Function App's Managed Identity
}

# If your module.test_module.principal_id refers to a different Service Principal/Managed Identity
# and that also needs access, you would create another role assignment for it:
resource "azurerm_role_assignment" "test_module_kv_access" {
  scope                = azurerm_key_vault.kv.id
  role_definition_name = "Key Vault Secrets User" # Or other appropriate role
  principal_id         = module.test_module.principal_id
}
By removing the access_policy block (or understanding it's ignored) and using azurerm_role_assignment instead, you'll correctly grant permissions according to the Azure RBAC model, which is the modern and preferred way to manage access to Key Vault.
```

```
2025-07-26T12:18:56Z   [Information]   Python HTTP trigger function processed a request.
2025-07-26T12:18:56Z   [Information]   No environment configuration found.
2025-07-26T12:18:56Z   [Information]   ManagedIdentityCredential will use App Service managed identity
2025-07-26T12:18:56Z   [Information]   Request URL: 'https://sgppipelinekv.vault.azure.net/secrets/test/?api-version=REDACTED'
Request method: 'GET'
Request headers:
    'Accept': 'application/json'
    'x-ms-client-request-id': '<some id>'
    'User-Agent': 'azsdk-python-keyvault-secrets/4.10.0 Python/3.12.10 (Linux-5.15.164.1-1.cm2-x86_64-with-glibc2.36)'
No body was attached to the request
2025-07-26T12:18:56Z   [Information]   Response status: 401
Response headers:
    'Cache-Control': 'no-cache'
    'Pragma': 'no-cache'
    'Content-Type': 'application/json; charset=utf-8'
    'Expires': '-1'
    'x-ms-keyvault-region': 'eastus'
    'x-ms-client-request-id': '<some id>'
    'x-ms-request-id': '<some id>'
    'x-ms-keyvault-service-version': '1.9.2584.1'
    'x-ms-keyvault-network-info': 'conn_type=Subnet;addr=172.24.0.179;act_addr_fam=InterNetworkV6;'
    'X-Content-Type-Options': 'REDACTED'
    'Strict-Transport-Security': 'REDACTED'
    'WWW-Authenticate': 'Bearer authorization="https://login.microsoftonline.com/<some id>", resource="https://vault.azure.net"'
    'Date': 'Sat, 26 Jul 2025 12:18:55 GMT'
    'Content-Length': '97'
2025-07-26T12:18:56Z   [Information]   Request URL: 'http://169.254.255.2:8081/msi/token?api-version=REDACTED&resource=REDACTED'
Request method: 'GET'
Request headers:
    'X-IDENTITY-HEADER': 'REDACTED'
    'Metadata': 'REDACTED'
    'User-Agent': 'azsdk-python-identity/1.23.1 Python/3.12.10 (Linux-5.15.164.1-1.cm2-x86_64-with-glibc2.36)'
No body was attached to the request
2025-07-26T12:18:56Z   [Information]   Response status: 400
Response headers:
    'Content-Type': 'application/json; charset=utf-8'
    'Date': 'Sat, 26 Jul 2025 12:18:55 GMT'
    'Server': 'Kestrel'
    'Transfer-Encoding': 'chunked'
    'X-CORRELATION-ID': 'REDACTED'
2025-07-26T12:18:56Z   [Warning]   DefaultAzureCredential failed to retrieve a token from the included credentials.
Attempted credentials:
	EnvironmentCredential: EnvironmentCredential authentication unavailable. Environment variables are not fully configured.
Visit https://aka.ms/azsdk/python/identity/environmentcredential/troubleshoot to troubleshoot this issue.
	ManagedIdentityCredential: App Service managed identity configuration not found in environment. invalid_scope
	SharedTokenCacheCredential: SharedTokenCacheCredential authentication unavailable. No accounts were found in the cache.
	AzureCliCredential: Azure CLI not found on path
	AzurePowerShellCredential: PowerShell is not installed
	AzureDeveloperCliCredential: Azure Developer CLI could not be found. Please visit https://aka.ms/azure-dev for installation instructions and then,once installed, authenticate to your Azure account using 'azd auth login'.
To mitigate this issue, please refer to the troubleshooting guidelines here at https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot.
2025-07-26T12:18:56Z   [Error]   Executed 'Functions.http_trigger' (Failed, Id=<some id>, Duration=157ms)
```

to solve the above error: https://stackoverflow.com/questions/78710321/how-to-connect-secrets-value-stored-in-azure-key-vault-to-azure-app-service-env

we need to set the environment variables in our function app so that when DefaultAzureCredentials() runs it loads these env variables as credentials

so the main thing is
- we need to set our managed identity of our azure function app to under system assigned to `on`
- we need to set azure key vault RBAC to have our account have a key vault administrator role in order to add access policies in the first place
- we need to have permission model in our AKV access configuration settings set to vault access policy
- we need to create an access policy that grants getting and listing secrets
- we need to set the principal of this application to be the managed identity of our azure function, e.g. if we search our azure function app name in the principal search box we will see it as it will have the same visible object id as our function app's managed identity's object id when we set its system assigned setting to `on`
- we need to create a secret in AKV and once done copy its secret identifier
- we go to our azure functions environment variables and add a new app application setting or env variable. We can it any name we want but what matters is that its corresponding value is set to `@Microsoft.KeyVault(SecretUri=<uri we copied earlier>)` where the secret identifier we just copied earlier which is usually in the form of `https://<our AKV name>.vault.azure.net/secrets/<our secret key name>/<our secret key id>`
- we will access this secret via the ff.

```
# once deployed to azure function app environment
# DefaultAzureCredential retrieves its client id
# and object id as important credentials to use for
# accessing the azure key vault
credential = DefaultAzureCredential()

secret_client = SecretClient(
    vault_url="https://sgppipelinekv.vault.azure.net",
    credential=credential
)

test = secret_client.get_secret('test')
```

- unfortunately sometimes we will need to add more secrets to azure keyvault but bhevause we set the permission model to vault access policy instead orf RBAC it will raise `The operation "List" is not enabled in this key vault's access policy.` when we go to our secrets tab in AKV. As a workaround we can revert back to the old permission model RBAC and once we create our keys we revert back to vault access policy
 

here because assuming we deployed our function `DefaultAzureCredential()` loads certain environment variables not visible to us that it uses to authenticate to AKV, which would be our managed identity

`secret_client.get_secret('test')` is the final phase where we retrieve the secret key we created using the name we set it to, which returns a secret object. To get the value of this secret we would have to use `.value` a getter of this object

https://learn.microsoft.com/en-us/answers/questions/1254022/getting-403-forbidden-access-is-denied-you-do-not

to list secrets under a vault access policy permission model we need to add another access policy with a principal that's not aour function app but the azure user itself...us. 

kaya di gumagana nung nagadd ka ng secrets and also added environment variables is because nagkamali ka ng name. It is good practice to always and always name your secret in azure key vault and your environment variable in the azure function app as the same. para pag inaccess using `secret_client.get_secret("<secretkey name>")` walang conflict

another issue is adding parameters in azure function apps. Because for some reason pag nagadd ng params nag reresult in internal server 500 error na naman. Pero no talagang nagerror kanina is kasi mali yung prior code statements

```
alright nice, I've configured this azure function to specifically be able to access secret keys from my key vault like tenant id, azure client secret, azure client id and subscription id so that my azure function can use these as credentials to generate a sas token that will be used to write to my blob storage account because as we know SAS is the best and most secure way to write to azure blob

That's an interesting approach, and it demonstrates a good understanding of how to use Key Vault to protect credentials!

However, your statement that "SAS is the best and most secure way to write to Azure Blob" in this specific scenario (an Azure Function writing to Blob Storage) is actually not the optimal or most secure method when Managed Identities are available.

Let's clarify why and what the preferred method is:

Understanding Your Current Setup:

Azure Function (with Managed Identity) -> securely gets Entra ID credentials (client ID, client secret, tenant ID) from Key Vault.

Azure Function uses these Entra ID credentials -> generates a SAS token.

Azure Function uses the SAS token -> writes to Azure Blob Storage.

Why this is not the most secure/optimal for Azure-to-Azure communication:

You've introduced an unnecessary layer of complexity and potential attack surface by generating a SAS token from Entra ID credentials within your Azure Function for an Azure-to-Azure call.

Overhead: You're managing Entra ID credentials (client ID, client secret) in Key Vault, retrieving them, and then using them to generate another credential (the SAS token). This adds more code, more points of failure, and more objects to manage.

Redundancy: The purpose of Managed Identities is to allow an Azure service (like your Function) to authenticate directly to other Azure services (like Blob Storage) using its own identity in Microsoft Entra ID, without needing any secrets or SAS tokens.

The Best and Most Secure Way for Azure Function to write to Azure Blob Storage:

The most secure and streamlined method for an Azure Function to write to Azure Blob Storage is using its Managed Identity with Azure Role-Based Access Control (RBAC) directly.

Here's how it works and why it's superior:

Enable Managed Identity for Azure Function: (You've already done this, great!) Azure automatically manages the identity and its credentials in Microsoft Entra ID.

Grant RBAC Role on Storage Account: Go to your Azure Storage Account in the Azure portal (or use Terraform/CLI) and navigate to "Access control (IAM)". Assign a suitable built-in RBAC role to your Azure Function's Managed Identity.

For writing data, the most common role is "Storage Blob Data Contributor".

For read-only, it would be "Storage Blob Data Reader."

Direct Authentication in Function Code: Your Function's code will then authenticate directly to Blob Storage using DefaultAzureCredential (or ManagedIdentityCredential explicitly if preferred). The Azure SDK automatically detects the Managed Identity and uses it for authentication.

Code Example (Conceptual Python):

Python

import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# No need to get client_id, client_secret, tenant_id from Key Vault for this!

# Get Storage Account URL (or connection string, though Managed Identity is better)
# You might pass this as an environment variable in the Function App settings
storage_account_url = os.environ["AZURE_STORAGE_ACCOUNT_URL"] # e.g., "https://yourstorageaccount.blob.core.windows.net"

try:
    # Authenticate using the Function's Managed Identity
    credential = DefaultAzureCredential()

    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=credential)

    # Get a client for the specific container
    container_client = blob_service_client.get_container_client("your-container-name")

    # Upload data
    blob_name = "your_file.txt"
    data = b"Hello, Azure Blob Storage from Managed Identity!"
    container_client.upload_blob(name=blob_name, data=data, overwrite=True)

    print(f"Successfully uploaded {blob_name} using Managed Identity.")

except Exception as ex:
    print(f"Error writing to blob storage: {ex}")

Why this is more secure and "best practice":

No Secret Handling: You completely eliminate the need for your Function to handle (retrieve from KV, generate with) client secrets or SAS tokens for this specific Azure-to-Azure interaction. Less secret handling = less risk.

Automatic Credential Rotation: The credentials of the Managed Identity are automatically managed and rotated by Azure AD, so you never have to worry about client secret expiry or manual rotation.

Least Privilege: RBAC allows you to grant very specific permissions (e.g., only "write" to blobs in a particular container) directly to your Function's identity.

Centralized Control: All permissions are managed centrally in Azure RBAC, which is auditable and consistent across Azure resources.

When are SAS Tokens still appropriate?

SAS tokens are excellent for:

Delegating access to external, untrusted clients: (e.g., a mobile app directly uploading photos, a browser downloading files). These clients usually don't have Azure AD identities.

Time-limited, granular access for specific operations: Providing temporary access for a specific task.

In summary, while your current setup works, for an Azure Function writing to Blob Storage, leveraging Managed Identities with direct RBAC permissions is the more secure, robust, and simpler solution. It cuts out the middleman of secret generation when it's not strictly necessary.
```

* a lot is connected to our azure function but sometimes we need to delete it to force an update to our code. So we have to redo the ff. again (this is assuming you tried `func azure functionapp publish <name of our function app resource>` as a last resort, because sometimes deploying via our azure extension pane may show a successful deployment, however running a more manual command like the former may reveal certain errors that may lie in our code case on point the reason why the code was not updating was because of the requirements.txt which included a pywin32 package where pip raised an error that a version of pywin32 package could not be found or that a dependency of some packages like urllib3 and conflicted with wrclib):
- create managed identity of function app again by enabling system assigned managed identity
- set CORS again of function app to `*`, `https://portal.azure.com`, `https://functions.azure.com`, `https://*.com`, and `http://*.com`
- add environment variables again of the same name as the secret keys created in the azure key vault and set to @Microsoft.KeyVault(SecretUri=<secret identifier>)
- delete old access policy in azure key vault tied to old function app and create another one with identity of new function app\
- delete old RBAC of old function app for azure blob storage and create another one using the system assigned managed identity of the new function app

* when setting up databricks cluster we may encounter a `virtual machine (VM) stock keeping unit (SKU) is not available in your region` error. We can run `az vm list-skus --location <region e.g. eastus, centralus, westus> --size <e.g. Standard_D, Standard_E, Standard_L, Standard_F, Standard_N> --all --output table` 

* Sometimes even when you already set the roles and permissions the unity catalog access connector's managed identity is allowed to have `dbutils.fs.ls("abfss://<container/file system name>@<storage account name>.dfs.core.windows.net/")` may still raise a `fs.azure.account_key` is missing indicating that databricks does not have sufficient permissions to access the container/file system. There may be causes to this but the most common is the ff: 
- we must be careful to enter the URL in creating the external location to where databricks would be reading, writing, listing, etc. files e.g. `abfss://<container/file system name>@<storage account name>.dfs.core.windows.net/`
- we must make sure our credential is created in our azure databricks catalog
- we must make sure the RBAC is set to the managed identity of the unity catalog access connector service


a ML Cluster with "no isolation shared" as access mode. This cluster is not compatible with unity. We set fs.azure.* variables in the cluster conf. like below to fix our issue:

fs.azure.account.oauth2.client.id.mydatalake.dfs.core.windows.net: {{secrets/mysecret/myclientid}}. 

Is there a better/proper way to do it ?

* reason why you get `Make sure the value of Authorization header is formed correctly including the signature` when accessing a newly created azure data lake storage container's files is because in RBAC we haven't added us the user ourselves to list the files in a container. We must add storage blob data contributor and storage queue data contributor as roles to our user account  



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

* azure managed identities: https://learn.microsoft.com/en-us/azure/ai-services/language-service/native-document-support/managed-identities
https://prashanth-kumar-ms.medium.com/azure-managed-identity-integration-with-storage-account-5bea9261a4d1
* generating shared access token to access the azure blob storage: https://learn.microsoft.com/en-us/azure/ai-services/translator/document-translation/how-to-guides/create-sas-tokens?tabs=Containers (this can be basically be generated using a post request using your microsoft entra id service principal)
https://learn.microsoft.com/en-us/rest/api/storageservices/create-user-delegation-sas#user-delegation-sas-support-for-directory-scoped-access 

* azure databricks cluster setup: https://medium.com/@phaneendraganji3/how-i-solved-the-vm-sku-not-available-in-your-region-error-while-creating-a-databricks-compute-fd8910247534