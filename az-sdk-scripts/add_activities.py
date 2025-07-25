from azure.identity import ClientSecretCredential
from azure.mgmt.datafactory.models import (
    LookupActivity, 
    LinkedService,
    CopyActivity
)

from datetime import datetime, timedelta
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import urlencode

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
    storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
    storage_account_key = os.environ.get("STORAGE_ACCOUNT_KEY")
    resource_group_name = os.environ.get("RESOURCE_GROUP_NAME")
