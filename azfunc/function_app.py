import time
import os
import azure.functions as func
import logging

from selenium import webdriver

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC

from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from azure.storage.filedatalake import DataLakeServiceClient, DataLakeDirectoryClient

from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from pathlib import Path

from utilities.loaders import download_dataset

# load env variables
env_dir = Path('../').resolve()
load_dotenv(os.path.join(env_dir, '.env'))


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

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
    # # define chrome options
    # chrome_options = ChromeOptions()
    # chrome_options.add_experimental_option('detach', True)
    
    # # arguments
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    
    # service = ChromeService(executable_path=ChromeDriverManager().install())
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    # driver.get('http://www.repository.voxforge1.org/downloads/SpeechCorpus/Trunk/Audio/Main/16kHz_16bit/')

    # # wait 5 seconds for page load
    # time.sleep(5)

    
    # driver.execute_script("window.scrollBy(0, document.body.scrollHeight)") 

    
    # anchor_tags = driver.find_elements(By.TAG_NAME, "a")

    # def helper(a_tag):
    #     # this will extract the href of all acnhor tags 
    #     link = a_tag.get_attribute('href')
    #     return link

    # # concurrently read and load all .json files
    # with ThreadPoolExecutor() as exe:
    #     links = list(exe.map(helper, anchor_tags))

    # # exclude all hrefs without .tgz extension
    # download_links = list(filter(lambda link: link.endswith('.tgz'), links))
    # n_links = len(download_links)


    # check if a parameter has been entered in the URL
    RANGE = req.params.get('range')
    if not RANGE:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            RANGE = req_body.get('range')
    # RANGE = n_links if not RANGE else int(RANGE)

    # # print(os.getcwd())
    # # download the raw .tgz files to azure data lake storages
    DATA_DIR = "C:/Users/LARRY/Documents/Scripts/data-engineering-path/signal-gender-predictor/include/data"
    # download_dataset(download_links[:RANGE], data_dir=DATA_DIR)

    # Retrieve credentials from environment variables
    tenant_id = os.environ.get("AZURE_TENANT_ID")
    client_id = os.environ.get("AZURE_CLIENT_ID")
    client_secret = os.environ.get("AZURE_CLIENT_SECRET")
    storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
    # print(f"tenant_id: {tenant_id}")
    # print(f"client_id: {client_id}")
    # print(f"client_secret: {client_secret}")


    credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
    # credential = DefaultAzureCredential()

    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=credential,
    )

    # get blob client
    containers = blob_service_client.list_containers()
    for container in containers:
        print(f"container: {container}")
    print(f"azure container: {container_client}")
    

    # Upload the file
    # with open(os.path.join(DATA_DIR, "1028-20100710-hne.tgz"), "rb") as data:
    #     container_client.upload_blob(name="test_signal.tgz", data=data, overwrite=True)

    # view files
    # https://sgppipelinesa.blob.core.windows.net/sgppipelinesa-bronze
    # https://sgppipelinesa.blob.core.windows.net/sgppipelinesa-bronze?restype=REDACTED&comp=REDACTED
    try:
        # get container client
        container_client = blob_service_client.get_container_client(container=f"{storage_account_name}-bronze") 
        blobs = container_client.get_container_access_policy()
        for blob in blobs:
            print(blob.name)
    except Exception as e:
        print(f"Error operating on blobs: {e}")

    # containers = blob_service_client.list_containers()
    # for container in containers:
    #     print(container)

    return func.HttpResponse(
        # f"This HTTP triggered function extracted {n_links} audio signals successfully: {download_links[:RANGE]}",
        f"This HTTP triggered the uploading of the signals to azure data lake storage",
        status_code=200
    )