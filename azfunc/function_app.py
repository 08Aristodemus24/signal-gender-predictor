from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from azure.storage.filedatalake import DataLakeServiceClient
from azure.keyvault.secrets import SecretClient

from datetime import datetime, timedelta
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import urlencode
from bs4 import BeautifulSoup

import time
import requests
import os
import azure.functions as func
import logging
import json
import re


# # this is strictly used only in development
# # load env variables
# env_dir = Path('../').resolve()
# load_dotenv(os.path.join(env_dir, '.env'))


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

def batch_signal_files_lookup(data: list, batch_size: int):
    """
    returns an iterator with a json object representing the
    all the base url and the relative url of the compressed
    audio recording/signal of a subject in an http resource
    """

    for i in range(0, len(data), batch_size):
        # get current batch of data
        curr_batch = data[i:i + batch_size]

        # construct the lookup dictionary that will be 
        # uploaded as json to adls2
        curr_batch_signal_files_lookup = [
            {
                "BaseURL": download_link,
                "RelativeURL": download_link.split("/")[-1],
                "FileName": download_link.split("/")[-1],
            } for download_link in curr_batch
        ]

        # convert dicitonary to json
        curr_batch_signal_files_lookup_json = json.dumps(
            curr_batch_signal_files_lookup, 
            indent=4
        ).encode("utf-8")

        # yield the json object
        yield curr_batch_signal_files_lookup_json

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # we need to set the environment variables in our function 
    # app so that when DefaultAzureCredentials() runs it loads 
    # the env variables in our azure function app service 
    # as credentials. This must include the name of the secret
    # we want to access set to a value @Microsoft.KeyVault(SecretUri=<copied-value>)
    # where `<copied value>` here is actually the secred identifier we
    # copied when we created our secret key and value pair azure key
    # vault. If this is not set even if azure key vault hgas an access
    # policy that grants the azure function to access it it will result
    # in a internal server 500 error
    credential = DefaultAzureCredential()

    # 
    secret_client = SecretClient(
        vault_url="https://sgppipelinekv.vault.azure.net",
        credential=credential
    )

    test = secret_client.get_secret('test')
    storage_account_name = secret_client.get_secret("StorageAccountName")

    # create client with generated sas token
    datalake_service_client = DataLakeServiceClient(
        account_url=f"https://{storage_account_name.value}.dfs.core.windows.net", 
        credential=credential
    )

    # retrieves file system client to retrieve datalake client
    # writes json file to the selected container. The 
    misc_container_client = datalake_service_client.get_file_system_client(f"{storage_account_name.value}-miscellaneous")

    # create test dicitonary to convert to json object
    test = [
        {
            "BaseURL": "http://www.repository.voxforge1.org/downloads/SpeechCorpus/Trunk/Audio/Main/16kHz_16bit/1028-20100710-hne.tgz",
            "RelativeURL": "1028-20100710-hne.tgz",
            "FileName": "1028-20100710-hne.tgz"
        },
        {
            "BaseURL": "http://www.repository.voxforge1.org/downloads/SpeechCorpus/Trunk/Audio/Main/16kHz_16bit/1337ad-20170321-ajg.tgz",
            "RelativeURL": "1337ad-20170321-ajg.tgz",
            "FileName": "1337ad-20170321-ajg.tgz"
        }
    ]
    test_json = json.dumps(test, indent=4).encode("utf-8")

    # create file in blob container and upload the json object
    test_client = misc_container_client.get_file_client("signal_files_lookup_test.json")
    test_client.upload_data(test_json, overwrite=True)

    # # listing containers/file system, directories, and paths/blobs
    # for fs in datalake_service_client.list_file_systems():
    #     print(f"file system name: {fs.name}")


    # container = datalake_service_client.get_file_system_client("sgppipelinesa-miscellaneous")
    # dir = container.get_directory_client("lookup_files")
    # print(f"directory name: {dir.path_name}")
    # files = dir.get_paths(recursive=True)
    # for file in files:
    #     print(file.name)

    
    # if there is a passed parameter get its value
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello {name}, your HTTP triggered function wrote test.json to storage container {storage_account_name.value}.")
    else:
        return func.HttpResponse(
            f"Hello, your HTTP triggered function wrote test.json to storage container {storage_account_name.value}.",
            status_code=200
        )
    
@app.route(route="extract_signals")
def extract_signals(req: func.HttpRequest) -> func.HttpResponse:
    response = requests.get("http://www.repository.voxforge1.org/downloads/SpeechCorpus/Trunk/Audio/Main/16kHz_16bit/")
    r_txt = str(response.text)
    pattern = r'<a\s+?href="([^"]*)"'
    links = re.findall(pattern, r_txt)
    download_links = list(filter(lambda link: link.endswith(".tgz") , links))

    # exclude all hrefs without .tgz extension
    # http://www.repository.voxforge1.org/downloads/SpeechCorpus/Trunk/Audio/Main/16kHz_16bit/1028-20100710-hne.tgz
    batched_signal_files_lookup_jsons = batch_signal_files_lookup(download_links, batch_size=5000)

    # get number of downloads
    n_links = len(download_links)
    
    # check if a parameter has been entered in the URL
    RANGE = req.params.get('range')
    if not RANGE:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            RANGE = req_body.get('range')
    RANGE = n_links if not RANGE else int(RANGE)

    # once deployed to azure function app environment
    # DefaultAzureCredential() retrieves the azure functions
    # managed identity we created when we enabled system 
    # assigned managed identity which assigns an object id
    # to our azure function app and in which we permitted this
    # object id in our azure key vault and azure blob storage 
    # to have access to these resources. This object id is what
    # we use to access these resources
    credential = DefaultAzureCredential()

    # pass this as credential to secret client as well
    # as our blob storage client later
    secret_client = SecretClient(
        vault_url="https://sgppipelinekv.vault.azure.net",
        credential=credential
    )

    # load secret keys from key vault
    test = secret_client.get_secret('test')
    storage_account_name = secret_client.get_secret('StorageAccountName')
    # resource_group_name = secret_client.get_secret('resource-group-name')
    
    # # Retrieve credentials from environment variables
    # storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
    # storage_account_key = os.environ.get("STORAGE_ACCOUNT_KEY")

    # account_sas_kwargs = {
    #     "account_name": storage_account_name,
    #     "account_key": storage_account_key,
    #     "services": Services(blob=True, queue=True, fileshare=True),
    #     "resource_types": ResourceTypes(
    #         service=True, 
    #         container=True, 
    #         object=True
    #     ), 
    #     "permission": AccountSasPermissions(
    #         read=True, 
    #         write=True,
    #         delete=True,
    #         list=True,
    #         add=True,
    #         create=True,
    #         update=True,
    #         process=True
    #     ), 
    #     "start": datetime.utcnow(),  
    #     "expiry": datetime.utcnow() + timedelta(days=1) 
    # } 
    
    # # generated sas token is at the level of the storage account, 
    # # permitting services like blobs, files, queues, and tables 
    # # to be read, listed, retrieved, updated, deleted etc. 
    # # where allowed resource types are service, container 
    # sas_token = generate_account_sas(**account_sas_kwargs)

    # begin writing files in blob storage
    try:
        # create client with generated sas token
        datalake_service_client = DataLakeServiceClient(
            account_url=f"https://{storage_account_name.value}.dfs.core.windows.net", 
            credential=credential
        )

        # retrieves file system client to retrieve datalake client
        # writes json file to the selected container. The 
        misc_container_client = datalake_service_client.get_file_system_client(f"{storage_account_name.value}-miscellaneous")
        
        # using newly created blob client we upload the json 
        # object as a file. There are 6321 items of these urls
        # in total
        for i, batch in enumerate(batched_signal_files_lookup_jsons):
            signal_files_lookup_client = misc_container_client.get_file_client(f"signal_files_lookup_{i + 1}.json")
            signal_files_lookup_client.upload_data(batch, overwrite=True)

    except Exception as e:
        print(f"Error operating on blobs: {e}")

    return func.HttpResponse(
        f"This HTTP triggered function extracted {n_links} audio signals successfully to storage account {storage_account_name.value}",
        status_code=200
    )