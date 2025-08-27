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

def print_item(group):
    """Print an Azure object instance."""
    print("\tName: {}".format(group.name))
    print("\tId: {}".format(group.id))
    if hasattr(group, 'location'):
        print("\tLocation: {}".format(group.location))
    if hasattr(group, 'tags'):
        print("\tTags: {}".format(group.tags))
    if hasattr(group, 'properties'):
        print_properties(group.properties)


def print_properties(props):
    """Print a ResourceGroup properties instance."""
    if props and hasattr(props, 'provisioning_state') and props.provisioning_state:
        print("\tProperties:")
        print("\t\tProvisioning State: {}".format(props.provisioning_state))
    print("\n\n")