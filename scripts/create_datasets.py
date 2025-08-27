from azure.identity import ClientSecretCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.mgmt.datafactory.models import (
    DatasetResource,
    
    LinkedServiceReference,
    SecureString,
    ParameterSpecification,
    ParameterType,

    AzureBlobFSDataset,
    HttpDataset,
    BinaryDataset,

    HttpSource,
    FileSystemSink,

    DatasetCompression,
    DatasetFolder
)

from dotenv import load_dotenv
from pathlib import Path

import os


def create_singal_files_lookup_datasets():
    # Create an Azure blob dataset (input)
    sgppipeline_adl2_source_dump_link = LinkedServiceReference(
        type="LinkedServiceReference", 
        reference_name="sgppipeline_adl2_source_dump_link"
    )

    file_system = f"{storage_account_name}-miscellaneous"
    directory = ""
    folder_path = os.path.join(file_system, directory).replace("\\", "/")
    file_name = "signal_files_lookup_test.json"
    signal_files_lookup_test = DatasetResource(
        properties=AzureBlobFSDataset(
            linked_service_name=sgppipeline_adl2_source_dump_link, 
            folder_path=folder_path,    
            file_name=file_name
        )
    )

    adf_client.datasets.create_or_update(
        resource_group_name=resource_group_name,
        factory_name=adf_name,
        dataset_name="signal_files_lookup_test.json",
        dataset=signal_files_lookup_test
    )


if __name__ == "__main__":
    # load env variables
    env_dir = Path('../').resolve()
    load_dotenv(os.path.join(env_dir, '.env'))

    # Retrieve credentials from environment variables
    tenant_id = os.environ.get("AZURE_TENANT_ID")
    client_id = os.environ.get("AZURE_CLIENT_ID")
    client_secret = os.environ.get("AZURE_CLIENT_SECRET")
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
    resource_group_name = os.environ.get("RESOURCE_GROUP_NAME")

    # get function app key and url
    function_app_url = os.environ.get("FUNCTION_APP_URL")
    function_app_key = os.environ.get("FUNCTION_APP_EXTRACT_SIGNALS_TEST_KEY")

    # get azure key vault base url
    key_vault_base_url = os.environ.get("KEY_VAULT_BASE_URL")

    # get azure storage account name
    storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
    storage_account_key = os.environ.get("STORAGE_ACCOUNT_KEY")
    storage_account_url = os.environ.get("STORAGE_ACCOUNT_URL")

    # location and data factory name
    location = "eastus"
    adf_name = "sgppipelineadf"

    # Specify your Active Directory client ID, client secret, and tenant ID
    credential = ClientSecretCredential(
        client_id=client_id, 
        client_secret=client_secret, 
        tenant_id=tenant_id
    )

    adf_client = DataFactoryManagementClient(credential, subscription_id)
    
    # creates multiple lookup file datasets
    # create_singal_files_lookup_datasets()

    # create source dataset for http files
    sgppipeline_http_source_link = LinkedServiceReference(
        type="LinkedServiceReference", 
        reference_name="sgppipeline_http_source_link"
    )
    """problem here is that RelativeURL doesn't appear
    only in HTTPDataset does it appear but using it I can't
    specify the file type of binary"""
    signal_files_source = DatasetResource(
        properties=BinaryDataset(
            linked_service_name=sgppipeline_http_source_link, 
            compression=DatasetCompression(
                type="TarGZip",
                level="Optimal"
            ),
            parameters={
                "BaseURL": ParameterSpecification(
                    type=ParameterType.STRING,
                    default_value=None
                ),
                "RelativeURL": ParameterSpecification(
                    type=ParameterType.STRING,
                    default_value=None
                ), 
            },
            additional_properties={
                "RelativeURL": {
                    "value": "@{dataset().RelativeURL}"
                }
            },
        )
    )

    adf_client.datasets.create_or_update(
        resource_group_name=resource_group_name,
        factory_name=adf_name,
        dataset_name="signal_files_source",
        dataset=signal_files_source
    )

    # create sink dataset for the unzipped files
    sgppipeline_adl2_source_dump_link = LinkedServiceReference(
        type="LinkedServiceReference", 
        reference_name="sgppipeline_adl2_source_dump_link"
    )

    signal_files_sink = DatasetResource(
        properties=AzureBlobFSDataset(
            linked_service_name=sgppipeline_adl2_source_dump_link, 
            folder_path=f"{storage_account_name}-bronze"
        )
    )

    adf_client.datasets.create_or_update(
        resource_group_name=resource_group_name,
        factory_name=adf_name,
        dataset_name="signal_files_sink",
        dataset=signal_files_sink
    )