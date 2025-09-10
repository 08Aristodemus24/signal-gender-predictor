import sys
import datetime as dt
import os
import shutil
import time

from pathlib import Path

from airflow import DAG, settings
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.papermill.operators.papermill import PapermillOperator
from airflow.models import Variable, Connection 
from airflow.configuration import conf

# go to this site if you want to use cron instead of datetime to set schedule_interval
# https://crontab.guru/#00_12_*_*_Sun




# get airflow folder
AIRFLOW_HOME = conf.get('core', 'dags_folder')

# base dir would be /opt/***/ or /opt/airflow
BASE_DIR = Path(AIRFLOW_HOME).resolve().parent

default_args = {
    'owner': 'mikhail',
    'retries': 3,
    'retry_delay': dt.timedelta(minutes=2)
}

with DAG(
    dag_id="sgp_pipeline",
    default_args=default_args,
    description="extract transfrom load raw audio recordings for predicting gender of audio recording",
    start_date=dt.datetime(2024, 1, 1, 12),

    # runs every sunday at 12:00 
    schedule="00 12 * * Sun",
    catchup=False
) as dag:
    

    extract_signals = BashOperator(
        task_id="extract_signals",
        bash_command=f"python {AIRFLOW_HOME}/operators/extract_signals.py"
    ) 

    ingest_signals = PapermillOperator(
        task_id="ingest_signals",
        input_nb=f"{AIRFLOW_HOME}/operators/ingest_signals.ipynb",
        output_nb=f"{BASE_DIR}/include/scripts/ingest_signals_out.ipynb",
        # parameters={"msgs": "Ran from Airflow at {{ logical_date }}!"},
    )

    ingest_labels = PapermillOperator(
        task_id="ingest_labels",
        input_nb=f"{AIRFLOW_HOME}/operators/ingest_labels.ipynb",
        output_nb=f"{BASE_DIR}/include/scripts/ingest_labels_out.ipynb",
    )

    second_stage_signal_transform = PapermillOperator(
        task_id="second_stage_signal_transform",
        input_nb=f"{AIRFLOW_HOME}/operators/second_stage_signal_transform.ipynb",
        output_nb=f"{BASE_DIR}/include/scripts/second_stage_signal_transform.ipynb",
    )

    third_stage_signal_transform = PapermillOperator(
        task_id="third_stage_signal_transform",
        input_nb=f"{AIRFLOW_HOME}/operators/third_stage_signal_transform.ipynb",
        output_nb=f"{BASE_DIR}/include/scripts/third_stage_signal_transform.ipynb",
    )

    augment_signals = PapermillOperator(
        task_id="augment_signals",
        input_nb=f"{AIRFLOW_HOME}/operators/augment_signals.ipynb",
        output_nb=f"{BASE_DIR}/include/scripts/augment_signals.ipynb",
    )

    select_signal_features = BashOperator(
        task_id="select_signal_features",
        bash_command=f"python {AIRFLOW_HOME}/operators/select_signal_features.py"
    )

    extract_signals >> [ingest_signals, ingest_labels]
    [ingest_signals, ingest_labels] >> second_stage_signal_transform 
    second_stage_signal_transform >> third_stage_signal_transform 
    third_stage_signal_transform >> augment_signals >> select_signal_features