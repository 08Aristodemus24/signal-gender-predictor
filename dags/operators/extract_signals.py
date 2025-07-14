from selenium import webdriver

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC

import time
import os

from utilities.loaders import download_dataset

from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor

# python ./operators/extract_signals.py --range 1 --data-dir ../include/data/
if __name__ == "__main__":
    print(f"current directory: {os.getcwd()}")
    
    # get year range and state from user input
    parser = ArgumentParser()
    parser.add_argument("--range", type=int, default=-1, help="represents the end range of what files to download")
    parser.add_argument("--data-dir", type=str, default="./include/data", help="represents the directory which to download the files")
    args = parser.parse_args()
    
    RANGE = args.range
    DATA_DIR = args.data_dir

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

    
    driver.execute_script("window.scrollBy(0, document.body.scrollHeight)") 

    
    anchor_tags = driver.find_elements(By.TAG_NAME, "a")

    def helper(a_tag):
        # this will extract the href of all acnhor tags 
        link = a_tag.get_attribute('href')
        return link

    # concurrently read and load all .json files
    with ThreadPoolExecutor() as exe:
        links = list(exe.map(helper, anchor_tags))

    # exclude all hrefs without .tgz extension
    download_links = list(filter(lambda link: link.endswith('.tgz'), links))

    # download the raw .tgz files to azure data lake storages
    download_dataset(download_links[:RANGE], data_dir=DATA_DIR)