from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC

from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,

    BlobSasPermissions,
    ContainerSasPermissions,
    AccountSasPermissions,
    Services,
    ResourceTypes,
    UserDelegationKey,
    generate_account_sas,
    generate_container_sas,
    generate_blob_sas,
)

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

import time
import requests
import os
import azure.functions as func
import logging
import json


# load env variables
env_dir = Path('../').resolve()
load_dotenv(os.path.join(env_dir, '.env'))


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

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
    
@app.route(route="extract_signals")
def extract_signals(req: func.HttpRequest) -> func.HttpResponse:
    # define chrome options
    chrome_options = ChromeOptions()
    chrome_options.add_experimental_option('detach', True)
    
    # arguments
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get('http://www.repository.voxforge1.org/downloads/SpeechCorpus/Trunk/Audio/Main/16kHz_16bit/')

    # wait 5 seconds for page load
    time.sleep(5)

    # scrolls down to very bottom
    driver.execute_script("window.scrollBy(0, document.body.scrollHeight)") 

    # extracts all anchor tags in page
    anchor_tags = driver.find_elements(By.TAG_NAME, "a")
    def helper(a_tag):
        # this will extract the href of all acnhor tags 
        link = a_tag.get_attribute('href')
        return link

    # concurrently read and load all .tgz files
    with ThreadPoolExecutor() as exe:
        links = list(exe.map(helper, anchor_tags))

    # exclude all hrefs without .tgz extension
    # http://www.repository.voxforge1.org/downloads/SpeechCorpus/Trunk/Audio/Main/16kHz_16bit/1028-20100710-hne.tgz
    download_links = list(filter(lambda link: link.endswith('.tgz'), links))
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

    # # print(os.getcwd())
    # # download the raw .tgz files to azure data lake storages
    DATA_DIR = "C:/Users/LARRY/Documents/Scripts/data-engineering-path/signal-gender-predictor/include/data"
    # download_dataset(download_links[:RANGE], data_dir=DATA_DIR)

    # Retrieve credentials from environment variables
    tenant_id = os.environ.get("AZURE_TENANT_ID")
    client_id = os.environ.get("AZURE_CLIENT_ID")
    client_secret = os.environ.get("AZURE_CLIENT_SECRET")
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
    storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
    storage_account_key = os.environ.get("STORAGE_ACCOUNT_KEY")
    resource_group_name = os.environ.get("RESOURCE_GROUP_NAME")
    # print(f"tenant_id: {tenant_id}")
    # print(f"client_id: {client_id}")
    # print(f"client_secret: {client_secret}")


    credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)

    account_sas_kwargs = {
        "account_name": storage_account_name,
        "account_key": storage_account_key,
        "services": Services(blob=True, queue=True, fileshare=True),
        "resource_types": ResourceTypes(
            service=True, 
            container=True, 
            object=True
        ), 
        "permission": AccountSasPermissions(
            read=True, 
            write=True,
            delete=True,
            list=True,
            add=True,
            create=True,
            update=True,
            process=True
        ), 
        "start": datetime.utcnow(),  
        "expiry": datetime.utcnow() + timedelta(days=1) 
    } 
    
    # generated sas token is at the level of the storage account, 
    # permitting services like blobs, files, queues, and tables 
    # to be read, listed, retrieved, updated, deleted etc. 
    # where allowed resource types are service, container 
    sas_token = generate_account_sas(**account_sas_kwargs)
    

    # Upload the file
    # with open(os.path.join(DATA_DIR, "1028-20100710-hne.tgz"), "rb") as data:
    #     container_client.upload_blob(name="test_signal.tgz", data=data, overwrite=True)

    # view filesr
    # https://sgppipelinesa.blob.core.windows.net/sgppipelinesa-bronze
    # https://sgppipelinesa.blob.coe.windows.net/sgppipelinesa-bronze?restype=REDACTED&comp=REDACTED
    try:
        # create client with generated sas token
        blob_service_client = BlobServiceClient(
            account_url=f"https://{storage_account_name}.blob.core.windows.net", 
            credential=sas_token
        )

        # retrieves container client to retrieve blob client
        misc_container_client = blob_service_client.get_container_client(f"{storage_account_name}-miscellaneous")
        
        # using newly created blob client we upload the json 
        # object as a file
        for i, batch in enumerate(batched_signal_files_lookup_jsons):
            signal_files_lookup_client = misc_container_client.get_blob_client(f"signal_files_lookup_{i + 1}.json")
            signal_files_lookup_client.upload_blob(batch, overwrite=True)



    except Exception as e:
        print(f"Error operating on blobs: {e}")


    return func.HttpResponse(
        # f"This HTTP triggered function extracted {n_links} audio signals successfully: {download_links[:RANGE]}",
        f"This HTTP triggered the uploading of the signals to azure data lake storage",
        status_code=200
    )