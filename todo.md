* <s>setup airflow</s>
* <s>setup azure account first</s>
* <s>setup first operator that will somehow download the files again locally first</s>
* <s>setup azure data lake storage first using terraform</s>
* I will need a script that downloads the zip files containing the raw audio to the data lake I setup with terraform create an azure function, azure databricks, or azure batch to download 
* modify first operator to download the files to the setup azure data lake storage

* if I can upload a file to azure data lake storage via function locally I can upload the file to azure data lake storage container using secret keys in azure key vault
* integrate azure key vault with azure function so that if the task of uploading a file to azure blob storage containers does need credentials then I don't need to access them locally.

* uploading a file from azure function can't be done but can be done using azure data factory copy task which copies a http resource directly to azure data lake storage or azure blob storage
* automate this whole process of setting up adf copying from http to "sink" (ADL2) using python code if possible (reference here: https://learn.microsoft.com/en-us/azure/data-factory/quickstart-create-data-factory-python), because the steps are the ff:
- we need all relative urls and base urls of the http resources
- we construct a dictionary containing these relative urls and base urls of the http resources and write it in a json file and upload it directly to a miscellaneous container in our azure data lake storage account. We can initially do this locally but we will have to at some point do this inside the azure function instead without having to rely on local environmetn secrets & variables. See this post here how to setup azure functions with azure key vault: https://medium.com/@dssc2022yt/accessing-azure-key-vault-secrets-with-azure-functions-2e651980f292
- once the dictionary has been uploaded as a .json file we will define our lookup activity/task in azure data factory, and set its source dataset to be the json file we uploaded in our azure blob storage. But to do this we will have to create a linked service
- now all this can be automated using azure-mgmt-datafactory python package which allows us to interact with the azure datafactory interface and service programmatically via the this sub azure-sdk, we can define the linked services we want so that we can specify our activities the source/origin of our dataset and what sink/destination. We can use LookupActivity(), LinkedService(), CopyActivity() to programmatically build our pipeline's tasks
- to automate this however we would need to 


# Setting up azure workspace
* create an azure account at 
* setup azure databricks service (data transformation)
basics:
 subscription:
  - azure subscription 1
 resource group:
  - `<some name or create new if there isn't>`
 workspace name:
  - `<some workspace name>`
 region:
  - (US) East US
  - ...
  - (US) West US
 pricing tier:
  - (premium if you are free trial is still running or $200 credits have not yet been used)
 managed resource group name:
networking:
encryption:
security & compliance:
tags:
review + create:

* setup azure storage account (data lake to store raw and transformed data)
basics:
 subscription:
  - azure subscription 1
 resource group:
  - `<some name or create new if there isn't>`
 storage account name:
  - `<some name>`
 region:
  - (US) East US
  - ...
  - (US) West US
 primary service:
  - azure blob storage or azure data lake storage gen 2 (ADLS)
  - azure files
  - other files
 performance:
  - standard
  - premium 
 redundancy:
  - locally redundant storage (LRS) 
  - geo redundant storage (GRS)
  - zone redundant storage
  - geo zone redundant storage 
 make read access data available in the event of regional unavailability
  - `<boolean set to true>`
advanced:
 require secure transfer for rest api operations:
  - `<boolean set to true>`
 allow enabling anonymous access on individual containers:
  - `<boolean set to false>`
 enable storage account key access:
  - `<boolean set to true>`
 default to micorsoft entra authorization in the azure portal:
  - `<boolean set to false>`
 minimum LTS version:
  - version 1.2
 permitted scope for copy operations:
  - from any storage account
 enable heirarchical name space:
  - boolean set to true
 enable sftp:
  - boolean set to false
 enable network file system v3:
  - boolean set to false
 allow cross tenant replication:
  - false

create containers or the equivalent of an s3 bucket in AWS. These containers will be bronze, silver, and gold representing the different stages of the data from extraction to transformation to preparation to loading i.e. raw extracted data will be in bronze container, the reformatted data and casted version of the data will be in silver, and the normalized and transformed data maybe features for machine learning or new columns or updated values for analyses will be in the gold container

* create azure synapse analytics service (DWH)
basics:
 subscription:
  - azure subscription 1
 resource group:
  - `<some name or create new if there isn't>`
 managed resource group:
  - `<some name>`
 workspace name:
  - `<>`
 region:
  - (US) East US
  - ...
  - (US) West US
 select data lake storage gen 2:
  - from subscription
  - manually via URL
 data lake storage gen 2 account name:
  - 
 data lake storage gen 2 account name:
  - bronze (container we created)
  - silver (container we created)
  - gold (container we created)
  - synapse fs

costs 5$ per terabyte in queries that we run

* configuring azure databricks to communicate with azure data lake storage to read data
create compute in azure databricks workspace (this is where apache spark essentially coomes in as it is the engine that azure databricks sits on top on)
policy:
 - unrestricted
node:
 - single node
 - multi node
access mode:
 - single user
single user access:
 - <some user>
databricks runtime version:
 - 15.4 LTS (scala 2.12, spark 3.5.0)
use photon acceleration:
 - boolean set to false
node type (specification of node memory and cores):
 - standard d3 v2 (14gb, 4cores)
 - ...
terminate after <n> minutes of inactivity:
 - boolean set to true

go to catalog > external data > credentials > create new storage credential
credential type:
 - azure managed identity
credential name:
 - <some name>
access connector ID: (go to created databricks workspace > managed resource group > unity catalog access connector > copy resource ID)
 - resource id copied from databricks

click create

go to catalog > external data > external locations > create new external location
external location name:
 - bronze
URL:
 - abfss://<container name>@<storage account name>.dfs.core.windows.net
storage credential:
 - the storage credential we jsut created

do this for all the containers we created 

* Add role assignment (equivalent to creating IAM role in aws to manage access to resources like s3)
go to storage accounts service again > access control (IAM) > add > search for storage blob > select storage blob data contributor in order to gain access to read, write, and delete permissions to the azure data lake storage containers we have which would be the bronze, silver, and gold ones
members:
 selected role:
  - storage blob data contributor
 assign access to:
  - user group or service principal
  - managed identity (pick this)
 members:
  select members:
   subscription:
    -
   managed identity:
    - access connector for azure databricks
    - all system assigned managed identities
    - synapse workspace
   select:
    - resource id we can copy in the unity catalog access connector in databricks workspace

this is equivalent to setting up permission policies for the s3 bucket in aws and setting up permission policies for IAM user which are completely separate

* create azure databricks notebook that will extract data and dump it into our azure data lake storage (ADLS)
how we essentially write files in spark is recall `<spark df>.write.<file type e.g. parquet or csv>(<file path>, mode="overwrite")` or `dbutils.fs.put(<file path>, <data e.g. json, csv, etc.>, overwrite=True)` the file path we must put is `abfss://<container name>@<storage account name>.dfs.core..windows.net` i.e. `abfss://bronze@michael.dfs.core.windows.net` in order to write the extracted/transformed data we have into our azure data lake storage

from here we just do our typical pyspark operations in transformation and write the final dataframe to ADLS 

* to orchestrate and automate this whole process we use azure data factory (ADF)

like airflows feature of its tasks being able to use return values from previous tasks called xcoms, ADF also has this feature 