from azure.identity import ClientSecretCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.mgmt.datafactory.models import (
    LookupActivity, 
    LinkedService,
    CopyActivity,
    
    LinkedServiceResource,
    AzureFunctionLinkedService,
    AzureKeyVaultLinkedService,
    SecureString,
    AzureBlobFSLinkedService,
    HttpLinkedService,
    ParameterSpecification,
    ParameterType,

    HttpDataset,
    AzureBlobFSDataset,
    HttpSource,
    FileSystemSink
)

from dotenv import load_dotenv
from pathlib import Path

import os



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

    # defining function app linked service
    sgppipeline_fa_link = LinkedServiceResource(
        properties=AzureFunctionLinkedService(
            function_app_url=function_app_url,
            authentication="Anonymous",
            function_key=SecureString(value=function_app_key),
        )
    )

    adf_client.linked_services.create_or_update(
        resource_group_name=resource_group_name,
        factory_name=adf_name,
        linked_service_name="sgppipeline_fa_link",
        linked_service=sgppipeline_fa_link
    )

    # by default goes with system assigned managed identity
    # as authentication method
    sgppipeline_akv_link = LinkedServiceResource(
        properties=AzureKeyVaultLinkedService(
            base_url=key_vault_base_url,
        )
    )

    adf_client.linked_services.create_or_update(
        resource_group_name=resource_group_name,
        factory_name=adf_name,
        linked_service_name="sgppipeline_akv_link",
        linked_service=sgppipeline_akv_link
    )

    # for creating a azure data lake storage gen 2 linked service
    # when key is specified authentication type becomes account 
    # key instead of system assigned managed identity automatically
    sgppipeline_adl2_source_dump_link = LinkedServiceResource(
        # azure blob file system (fs) is adl2's linked service
        properties=AzureBlobFSLinkedService(
            url=storage_account_url,
            account_key=storage_account_key,
            tenant=tenant_id,
        )
    )

    adf_client.linked_services.create_or_update(
        resource_group_name=resource_group_name,
        factory_name=adf_name,
        linked_service_name="sgppipeline_adl2_source_dump_link",
        linked_service=sgppipeline_adl2_source_dump_link
    )

    # creates linked service for http based applications
    sgppipeline_http_source_link = LinkedServiceResource(
        properties=HttpLinkedService(
            # we need to wrap value in @{} if we ever want it
            # to be dynamic
            url="@{linkedService().BaseURL}",
            authentication_type="Anonymous",
            parameters={
                "BaseURL": ParameterSpecification(
                    type=ParameterType.STRING,
                    default_value=None
                )
            },
            enable_server_certificate_validation=True
        )
    )

    adf_client.linked_services.create_or_update(
        resource_group_name=resource_group_name,
        factory_name=adf_name,
        linked_service_name="sgppipeline_http_source_link",
        linked_service=sgppipeline_http_source_link
    )
