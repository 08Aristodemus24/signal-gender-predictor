# Now that all necessary data have now been extracted, 
# transformed, dumped in a lake (AWS S3) as parquet files,
# we can then load this in an in-process OLAP DB like duckdb
# /motherduck 
import duckdb
import os

# from duckdb.typing import DuckDBPyConnection
from dotenv import load_dotenv
from pathlib import Path


def create_and_connect_to_db(conn, db_name: str="signal_gender_predictor_db"):
    # create a database if there's not one that already exists
    conn.sql(f"""CREATE DATABASE IF NOT EXISTS {db_name}""")
    conn.sql(f"""USE {db_name}""")


def load_externals(conn, conn_str: str):
    # installing dependencies and creating secrets object
    conn.sql(f"""INSTALL azure""")
    conn.sql(f"""LOAD azure""")
    conn.sql(f"""
        CREATE OR REPLACE SECRET az_sgp (
            TYPE azure,
            CONNECTION_STRING '{conn_str}'
        );
    """)
    # the is required if this notebook is run in linux environment
    # like airflow container
    conn.sql("SET azure_transport_option_type = 'curl'")

def load_feature_list(conn: duckdb.DuckDBPyConnection, MISCELLANEOUS_DATA_DIR: str, MISCELLANEOUS_FOLDER_NAME: str, FILE_NAME: str):
    # create json path existing in adl2
    selected_feats_path = os.path.join(
        MISCELLANEOUS_DATA_DIR.format(
            FOLDER_NAME=MISCELLANEOUS_FOLDER_NAME,
        ),
        FILE_NAME
    ).replace("\\", "/")
    print(f"reading selected features path {selected_feats_path}...")
    
    selected_feats = [feature[-1] for feature in conn.sql(f"""
        SELECT * FROM read_json('{selected_feats_path}');
    """).fetchall()]
    
    return selected_feats

def load_signal_features(conn: duckdb.DuckDBPyConnection, selected_feats: list, table_name: str, GOLD_DATA_DIR: str, GOLD_FOLDER_NAME: str, FILE_NAME: str):
    # create table path existing in adl2
    table_path = os.path.join(
        GOLD_DATA_DIR.format(
            FOLDER_NAME=GOLD_FOLDER_NAME,
        ),
        FILE_NAME
    ).replace("\\", "/")
    print(f"reading table {table_path}...")

    # pass the path of this table so that it can be read
    print(conn.sql(f"""
            SELECT {", ".join(selected_feats)}, label FROM read_parquet('{table_path}')
    """))

if __name__ == "__main__":
    # Load azure credentials in order for duck db to read parquet files in adl2 gold layer 

    # use this only in development
    print("loading env variables...")
    env_dir = Path('../../').resolve()
    load_dotenv(os.path.join(env_dir, '.env'))
    print("env variables loaded.\n")
    storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
    credential = os.environ.get("STORAGE_ACCOUNT_KEY")
    conn_str = os.environ.get("STORAGE_ACCOUNT_CONN_STR")
    motherduck_token = os.environ.get("MOTHERDUCK_TOKEN")

    # use this path if the files are stored in a 
    # cloud provider 
    URL = f"abfss://{{FOLDER_NAME}}@{storage_account_name}.dfs.core.windows.net"
    GOLD_FOLDER_NAME = f"{storage_account_name}-gold"
    MISCELLANEOUS_FOLDER_NAME = f"{storage_account_name}-miscellaneous"

    # duckdb:///md:signal_gender_predictor_db
    print("connecting to duckdb...")
    conn = duckdb.connect("md:", config={"motherduck_token": motherduck_token})
    print("connected to duckdb.\n")

    # print(conn.sql("""SELECT CURRENT_DATABASE()"""))
    # create a database
    create_and_connect_to_db(conn, db_name="signal_gender_predictor_db")

    # load externals
    load_externals(conn, conn_str)
    
    # get extracted feature list
    selected_feats = load_feature_list(conn, URL, MISCELLANEOUS_FOLDER_NAME, "selected_feats.json")
    print(selected_feats)

    # load features
    load_signal_features(conn, selected_feats, "train_data_sc_sm", URL, GOLD_FOLDER_NAME, "train_data_sc_sm.parquet")
    load_signal_features(conn, selected_feats, "val_data_sc_sm", URL, GOLD_FOLDER_NAME, "val_data_sc_sm.parquet")
    load_signal_features(conn, selected_feats, "test_data_sc_sm", URL, GOLD_FOLDER_NAME, "test_data_sc_sm.parquet")

    # print(conn.sql("""SELECT CURRENT_DATABASE()"""))

    