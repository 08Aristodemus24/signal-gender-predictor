from selenium import webdriver

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC

import time
import selenium

from argparse import ArgumentParser
from utilities.loaders import download_dataset

from concurrent.futures import ThreadPoolExecutor


def extract_links(anchor_tags: list):
    """
    extract the href attribute values from list of anchor
    tags
    """

    def helper(a_tag):
        # this will extract the href of all acnhor tags 
        link = a_tag.get_attribute('href')
        return link

    # concurrently read and load all .json files
    with ThreadPoolExecutor() as exe:
        links = list(exe.map(helper, anchor_tags))

    return links


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-d", type=str, help="represents the directory ocntaining the zip files")
    args = parser.parse_args()
    DATA_DIR = args.d

    # options
    chrome_options = ChromeOptions()
    
    # arguments
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage") 

    # service
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get('http://www.repository.voxforge1.org/downloads/SpeechCorpus/Trunk/Audio/Main/16kHz_16bit/')

    # delay 5 seconds
    time.sleep(5)

    # scroll down to very end
    driver.execute_script("window.scrollBy(0, document.body.scrollHeight)") 

    # find a tags
    anchor_tags = driver.find_elements(By.TAG_NAME, "a")
    
    # extract hrefs from tags
    links = extract_links(anchor_tags)
    
    # exclude all hrefs without .tgz extension
    download_links = list(filter(lambda link: link.endswith('.tgz'), links))

    download_dataset(download_links, data_dir=DATA_DIR)