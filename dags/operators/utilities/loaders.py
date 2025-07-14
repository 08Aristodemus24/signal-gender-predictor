import requests
import zipfile
import tarfile
import os
# import librosa
import numpy as np
import pandas as pd
import re
import pickle
import json

from concurrent.futures import ThreadPoolExecutor



def download_dataset(urls: list | set, data_dir="./include/data"):

    def helper(url):
        file_name = url.split('/')[-1]

        print(file_name)
        response = requests.get(url, stream=True)

        # download the file given the urls
        FILE_PATH = os.path.join(data_dir, file_name)
        print(FILE_PATH)
        with open(FILE_PATH, mode="wb") as file:
            for chunk in response.iter_content(chunk_size=10 * 1024):
                file.write(chunk)

    # concurrently download the files given url
    with ThreadPoolExecutor(max_workers=5) as exe:
        exe.map(helper, urls)