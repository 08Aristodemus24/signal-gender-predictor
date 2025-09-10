# # Finally run feature selection on the newly synthesized data points and return only the columns which have the most importance

import os
import io
import random
import numpy as np
import matplotlib.pyplot as plt
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrowfs_adlgen2 as pa_adl
import json

from dotenv import load_dotenv
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE

from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.storage.filedatalake import DataLakeServiceClient, FileSystemClient


if __name__ == "__main__":
    # # local
    # DATA_DIR = "../include/data"

    
    # SILVER_FOLDER_NAME = "silver"
    # SUB_FOLDER_NAME = "stage-04"
    # SILVER_DATA_DIR = os.path.join("{DATA_DIR}", "{FOLDER_NAME}", "{SUB_FOLDER_NAME}").replace("\\", "/")
    # SILVER_DATA_DIR

    # # load credentials for cloud

    # # Retrieve credentials from environment variables
    # # this is strictly used only in development
    # # load env variables
    # env_dir = Path('../../').resolve()
    # load_dotenv(os.path.join(env_dir, '.env'))

    storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
    credential = os.environ.get("STORAGE_ACCOUNT_KEY")
    conn_str = os.environ.get("STORAGE_ACCOUNT_CONN_STR")

    # cloud
    # URL = "abfss://{FOLDER_NAME}@sgppipelinesa.dfs.core.windows.net"
    URL = "{FOLDER_NAME}"
    SILVER_FOLDER_NAME = "sgppipelinesa-silver"
    SUB_FOLDER_NAME = "stage-04"
    SILVER_DATA_DIR = os.path.join(URL, "{SUB_FOLDER_NAME}").replace("\\", "/")

    # # this client is for saving .pkl, .json files to ADL2

    # cloud
    # create client with generated sas token
    datalake_service_client = DataLakeServiceClient(
        account_url=f"https://{storage_account_name}.dfs.core.windows.net", 
        credential=credential
    )

    # retrieves file system client/container client 
    # to retrieve datalake client
    misc_container_client = datalake_service_client.get_file_system_client(f"{storage_account_name}-miscellaneous")

    # # this client is for saving pyarrow tables to ADL2 
    handler = pa_adl.AccountHandler.from_account_name(storage_account_name, credential=credential)
    fs = pa.fs.PyFileSystem(handler)

    # # read the data

    # cloud
    train_data_sc_sm_table_path = os.path.join(
        SILVER_DATA_DIR.format(
            FOLDER_NAME=SILVER_FOLDER_NAME,
            SUB_FOLDER_NAME=SUB_FOLDER_NAME
        ),
        "train_data_sc_sm.parquet"
    ).replace("\\", "/")
    train_data_sc_sm_table = pq.read_table(train_data_sc_sm_table_path, filesystem=fs)

    # # local
    # train_data_sc_sm_table_path = os.path.join(
    #     SILVER_DATA_DIR.format(
    #         DATA_DIR=DATA_DIR,
    #         FOLDER_NAME=SILVER_FOLDER_NAME,
    #         SUB_FOLDER_NAME=SUB_FOLDER_NAME
    #     ),
    #     "train_data_sc_sm.parquet"
    # ).replace("\\", "/")
    # train_data_sc_sm_table = pq.read_table(train_data_sc_sm_table_path)

    # cloud
    val_data_sc_sm_table_path = os.path.join(
        SILVER_DATA_DIR.format(
            FOLDER_NAME=SILVER_FOLDER_NAME,
            SUB_FOLDER_NAME=SUB_FOLDER_NAME
        ),
        "val_data_sc_sm.parquet"
    ).replace("\\", "/")
    val_data_sc_sm_table = pq.read_table(val_data_sc_sm_table_path, filesystem=fs)

    # # local
    # val_data_sc_sm_table_path = os.path.join(
    #     SILVER_DATA_DIR.format(
    #         DATA_DIR=DATA_DIR,
    #         FOLDER_NAME=SILVER_FOLDER_NAME,
    #         SUB_FOLDER_NAME=SUB_FOLDER_NAME
    #     ),
    #     "val_data_sc_sm.parquet"
    # ).replace("\\", "/")
    # val_data_sc_sm_table = pq.read_table(val_data_sc_sm_table_path)

    # cloud
    test_data_sc_sm_table_path = os.path.join(
        SILVER_DATA_DIR.format(
            FOLDER_NAME=SILVER_FOLDER_NAME,
            SUB_FOLDER_NAME=SUB_FOLDER_NAME
        ),
        "test_data_sc_sm.parquet"
    ).replace("\\", "/")
    test_data_sc_sm_table = pq.read_table(test_data_sc_sm_table_path, filesystem=fs)

    # # local
    # test_data_sc_sm_table_path = os.path.join(
    #     SILVER_DATA_DIR.format(
    #         DATA_DIR=DATA_DIR,
    #         FOLDER_NAME=SILVER_FOLDER_NAME,
    #         SUB_FOLDER_NAME=SUB_FOLDER_NAME
    #     ),
    #     "test_data_sc_sm.parquet"
    # ).replace("\\", "/")
    # test_data_sc_sm_table = pq.read_table(test_data_sc_sm_table_path)

    feat_cols = list(filter(lambda feat_col: not "label" in feat_col, train_data_sc_sm_table.column_names))

    train_output_sm = train_data_sc_sm_table.select(["label"]).to_pandas().to_numpy().ravel()
    train_input_sc_sm = train_data_sc_sm_table.select(feat_cols).to_pandas().to_numpy()

    val_output_sm = val_data_sc_sm_table.select(["label"]).to_pandas().to_numpy().ravel()
    val_input_sc_sm = val_data_sc_sm_table.select(feat_cols).to_pandas().to_numpy()

    test_output_sm = test_data_sc_sm_table.select(["label"]).to_pandas().to_numpy().ravel()
    test_input_sc_sm = test_data_sc_sm_table.select(feat_cols).to_pandas().to_numpy()

    if not misc_container_client.get_file_client("selected_feats.json").exists():
        n_features = 60

        # select best features first by means of backward
        # feature selection based on support vector classifiers
        model = RandomForestClassifier(verbose=0)
        selector = RFE(
            estimator=model, 
            n_features_to_select=n_features, 
            verbose=1,
            # we eliminate 5 features
            step=5
        )

        # train feature selector on data
        selector.fit(train_input_sc_sm, train_output_sm)

        # obtain feature mask boolean values, and use it as index
        # to select only the columns that have been selected by BFS
        # this is a list of boolean values
        feat_mask = selector.get_support().tolist()

        selected_feats = [item for item, included in zip(feat_cols, feat_mask) if included]

        selected_feats_json = json.dumps(selected_feats)
        selected_feats_json_body = selected_feats_json.encode('utf8')

        # # dump the selected features to .json in azure data lake

        # cloud
        json_file_client = misc_container_client.get_file_client("selected_feats.json")  
        json_file_client.upload_data(selected_feats_json_body, overwrite=True)

    # local
    MISCELLANEOUS_FOLDER_NAME = "miscellaneous"
    MISCELLANEOUS_DATA_DIR = os.path.join("{DATA_DIR}", "{FOLDER_NAME}").replace("\\", "/")

    # # local
    # with open(
    #     file=os.path.join(
    #         MISCELLANEOUS_DATA_DIR.format(
    #             DATA_DIR=DATA_DIR,
    #             FOLDER_NAME=MISCELLANEOUS_FOLDER_NAME,
    #         ),
    #         "selected_feats.json"
    #     ).replace("\\", "/"), 
    #     mode="w+"
    # ) as f:
    #     f.write(selected_feats_json)

    # # read the dumped .json containing the selected features in ADL2 miscellaneous layer

    # cloud
    json_file_client = misc_container_client.get_file_client("selected_feats.json")  
    download = json_file_client.download_file()
    downloaded_bytes = download.readall()
    selected_feats = json.loads(downloaded_bytes.decode('utf-8'))

    # # local
    # with open(
    #     file=os.path.join(
    #         MISCELLANEOUS_DATA_DIR.format(
    #             DATA_DIR=DATA_DIR, 
    #             FOLDER_NAME=MISCELLANEOUS_FOLDER_NAME
    #         ),
    #         "selected_feats.json"
    #     ).replace("\\", "/"), 
    #     mode="r"
    # ) as f:
    #     selected_feats = json.load(f)

    # # we use the selected features here to reduce the tables of each data split

    cols = selected_feats + ["label"]
    train_data_sc_sm_red_table = train_data_sc_sm_table.select(cols)
    val_data_sc_sm_red_table = val_data_sc_sm_table.select(cols)
    test_data_sc_sm_red_table = test_data_sc_sm_table.select(cols)

    # # save the final scaled, augmented, and reduced features to the gold layer

    # # local
    # GOLD_FOLDER_NAME = "gold"
    # GOLD_DATA_DIR = os.path.join("{DATA_DIR}", "{FOLDER_NAME}").replace("\\", "/")
    # SAVE_DIR = GOLD_DATA_DIR.format(
    #     DATA_DIR=DATA_DIR,
    #     FOLDER_NAME=GOLD_FOLDER_NAME,
    # )
    # SAVE_DIR

    # # local
    # train_data_sc_sm_red_table_path = os.path.join(
    #     SAVE_DIR,
    #     "train_data_sc_sm_red.parquet"
    # ).replace("\\", "/")
    # train_data_sc_sm_red_table_path

    # # local
    # val_data_sc_sm_red_table_path = os.path.join(
    #     SAVE_DIR,
    #     "val_data_sc_sm_red.parquet"
    # ).replace("\\", "/")
    # val_data_sc_sm_red_table_path

    # # local
    # test_data_sc_sm_red_table_path = os.path.join(
    #     SAVE_DIR,
    #     "test_data_sc_sm_red.parquet"
    # ).replace("\\", "/")
    # test_data_sc_sm_red_table_path

    # # local
    # pq.write_table(train_data_sc_sm_red_table, train_data_sc_sm_red_table_path)
    # pq.write_table(val_data_sc_sm_red_table, val_data_sc_sm_red_table_path)
    # pq.write_table(test_data_sc_sm_red_table, test_data_sc_sm_red_table_path)

    # cloud
    GOLD_FOLDER_NAME = "sgppipelinesa-gold"
    GOLD_DATA_DIR = os.path.join("{FOLDER_NAME}").replace("\\", "/")
    SAVE_DIR = GOLD_DATA_DIR.format(
        FOLDER_NAME=GOLD_FOLDER_NAME,
    )

    # cloud
    train_data_sc_sm_red_table_path = os.path.join(
        SAVE_DIR,
        "train_data_sc_sm_red.parquet"
    ).replace("\\", "/")

    # cloud
    val_data_sc_sm_red_table_path = os.path.join(
        SAVE_DIR,
        "val_data_sc_sm_red.parquet"
    ).replace("\\", "/")

    # cloud
    test_data_sc_sm_red_table_path = os.path.join(
        SAVE_DIR,
        "test_data_sc_sm_red.parquet"
    ).replace("\\", "/")

    # cloud
    pq.write_table(train_data_sc_sm_red_table, train_data_sc_sm_red_table_path, filesystem=fs)
    pq.write_table(val_data_sc_sm_red_table, val_data_sc_sm_red_table_path, filesystem=fs)
    pq.write_table(test_data_sc_sm_red_table, test_data_sc_sm_red_table_path, filesystem=fs)


