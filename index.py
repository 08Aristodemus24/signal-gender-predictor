from azure.storage.filedatalake import DataLakeServiceClient
from typing import Annotated
from fastapi import FastAPI, File, UploadFile, Body
from pydantic import BaseModel

import numpy as np
import librosa
import pyarrow as pa
import pyarrow.parquet as pq
import duckdb
import json
import os
import io
import pickle
import ydf

from scipy.stats import kurtosis as kurt, mode, skew, entropy
from dotenv import load_dotenv
from pathlib import Path

app = FastAPI()

models = {
    "signal-gender-predictor": {
        # "model":
        # "scaler":
        # "selected_feats":
    }
}


# load miscellaneous
def load_miscs():
    # Retrieve credentials from environment variables
    # this is strictly used only in development
    # load env variables
    env_dir = Path('./').resolve()
    load_dotenv(os.path.join(env_dir, '.env'))

    # load credentials
    storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
    credential = os.environ.get("STORAGE_ACCOUNT_KEY")
    conn_str = os.environ.get("STORAGE_ACCOUNT_CONN_STR")

    # cloud
    # create client with generated sas token
    datalake_service_client = DataLakeServiceClient(
        account_url=f"https://{storage_account_name}.dfs.core.windows.net", 
        credential=credential
    )

    # retrieves file system client/container client 
    # to retrieve datalake client
    misc_container_client = datalake_service_client.get_file_system_client(f"{storage_account_name}-miscellaneous")

    # cloud
    # loading the selected_feats.json file
    json_file_client = misc_container_client.get_file_client("selected_feats.json")  
    download = json_file_client.download_file()
    downloaded_bytes = download.readall()
    selected_feats = json.loads(downloaded_bytes.decode('utf-8'))

    # loading the scaler.pkl file
    scaler_file_client = misc_container_client.get_file_client("scaler.pkl")
    download = scaler_file_client.download_file()
    downloaded_bytes = download.readall()
    scaler = pickle.loads(downloaded_bytes)

    # redefine models as global variable
    global models

    # assign new values to the variable which will be
    # the scaler for our computed features and the selected
    # features to reduce the computed features
    models["signal-gender-predictor"]["scaler"] = scaler
    models["signal-gender-predictor"]["selected_feats"] = selected_feats


# load models
def load_models():
    # load ydf model
    signal_gender_predictor = ydf.load_model("./include/models/signal-gender-predictor")
    
    global models
    models["signal-gender-predictor"]["model"] = signal_gender_predictor

load_miscs()
load_models()




def extract_spectogam_stats(spectogram):
    """
    extracts statistical features of mel frequency ceptstral 
    coefficients, mel spectogram, mel decibel spectogram,
    spectral contrast spectogram matrices along the the x-axis
    so if a matrix or spectogram is (90, 35) final array will 
    be (1, 35)
    """

    # central tendency
    spec_mean = np.mean(spectogram, axis=0)
    spec_median = np.median(spectogram, axis=0)
    spec_mode = mode(spectogram, axis=0).mode
    spec_mode_cnt = mode(spectogram, axis=0).count
    
    # spread
    spec_min = np.min(spectogram, axis=0)
    spec_max = np.max(spectogram, axis=0)
    spec_range = spec_max - spec_min
    spec_var = np.var(spectogram, axis=0)
    spec_std = np.std(spectogram, axis=0)

    # percentiles
    spec_first_quart = np.percentile(spectogram, 25, axis=0)
    spec_third_quart = np.percentile(spectogram, 75, axis=0)
    spec_inter_quart_range  = spec_third_quart - spec_first_quart

    # morphology
    spec_entropy = entropy(spectogram, axis=0)
    spec_kurt = kurt(spectogram, axis=0)
    spec_skew = skew(spectogram, axis=0)

    return (
        spec_mean, 
        spec_median, 
        spec_mode, 
        spec_mode_cnt, 
        spec_min, 
        spec_max, 
        spec_range, 
        spec_var, 
        spec_std, 
        spec_first_quart, 
        spec_third_quart, 
        spec_inter_quart_range, 
        spec_entropy, 
        spec_kurt, 
        spec_skew
    )

def compute_statistical_feats(conn, subject_table, samples_per_win_size, samples_per_hop_size):
    

    # count = conn.sql("""
    #     SELECT COUNT(rowId) FROM subject_table
    # """).fetchall()[-1][-1]

    conn.sql(f"""
        CREATE OR REPLACE TEMPORARY TABLE subject_features AS (
            SELECT
                -- signals, 
                subjectId, 
                -- rowId,
                KURTOSIS(signals) OVER(PARTITION BY subjectId ORDER BY rowId ROWS BETWEEN CURRENT ROW AND {samples_per_win_size - 1} FOLLOWING) AS freq_kurt,
                SKEWNESS(signals) OVER(PARTITION BY subjectId ORDER BY rowId ROWS BETWEEN CURRENT ROW AND {samples_per_win_size - 1} FOLLOWING) AS freq_skew,
                ENTROPY(signals)OVER(PARTITION BY subjectId ORDER BY rowId ROWS BETWEEN CURRENT ROW AND {samples_per_win_size - 1} FOLLOWING) AS freq_entropy,
                AVG(signals) OVER(PARTITION BY subjectId ORDER BY rowId ROWS BETWEEN CURRENT ROW AND {samples_per_win_size - 1} FOLLOWING) AS freq_mean,
                MEDIAN(signals) OVER(PARTITION BY subjectId ORDER BY rowId ROWS BETWEEN CURRENT ROW AND {samples_per_win_size - 1} FOLLOWING) AS freq_median,
                MODE(signals) OVER(PARTITION BY subjectId ORDER BY rowId ROWS BETWEEN CURRENT ROW AND {samples_per_win_size - 1} FOLLOWING) AS freq_mode,
                MIN(signals) OVER(PARTITION BY subjectId ORDER BY rowId ROWS BETWEEN CURRENT ROW AND {samples_per_win_size - 1} FOLLOWING) AS freq_min,
                MAX(signals) OVER(PARTITION BY subjectId ORDER BY rowId ROWS BETWEEN CURRENT ROW AND {samples_per_win_size - 1} FOLLOWING) AS freq_max,
                VAR_SAMP(signals) OVER(PARTITION BY subjectId ORDER BY rowId ROWS BETWEEN CURRENT ROW AND {samples_per_win_size - 1} FOLLOWING) AS freq_var,
                STDDEV_SAMP(signals) OVER(PARTITION BY subjectId ORDER BY rowId ROWS BETWEEN CURRENT ROW AND {samples_per_win_size - 1} FOLLOWING) AS freq_stddev,
                QUANTILE_CONT(signals, 0.25) OVER(PARTITION BY subjectId ORDER BY rowId ROWS BETWEEN CURRENT ROW AND {samples_per_win_size - 1} FOLLOWING) AS freq_first_quart,
                QUANTILE_CONT(signals, 0.75) OVER(PARTITION BY subjectId ORDER BY rowId ROWS BETWEEN CURRENT ROW AND {samples_per_win_size - 1} FOLLOWING) AS freq_third_quart
            FROM subject_table
            WHERE (rowId % {samples_per_hop_size}) = 0
            ORDER BY rowId
        )
    """)

    conn.sql(f"""
        CREATE OR REPLACE TEMPORARY TABLE subject_features AS (
            SELECT 
                *,
                (freq_max - freq_min) AS freq_range,
                (freq_third_quart - freq_first_quart) AS freq_inter_quart_range
            FROM subject_features
        )
    """)

    subject_features = conn.sql(f"""
        SELECT * FROM subject_features
    """).to_arrow_table()

    return subject_features

def compute_spectral_features(subject_features, x_signals, hertz, samples_per_win_size, samples_per_hop_size, n_frames):
    zcr = librosa.feature.zero_crossing_rate(
        y=x_signals, 
        frame_length=samples_per_win_size, 
        hop_length=samples_per_hop_size
    )[:, :n_frames]
    poly_feats = librosa.feature.poly_features(
        y=x_signals, 
        sr=hertz, 
        n_fft=samples_per_win_size, 
        hop_length=samples_per_hop_size
    )[:, :n_frames]

    mel_spec = librosa.feature.melspectrogram(
        y=x_signals, 
        sr=hertz, 
        n_fft=samples_per_win_size, 
        hop_length=samples_per_hop_size, 
        n_mels=90
    )[:, :n_frames]
    mel_spec_mean, \
    mel_spec_median, \
    mel_spec_mode, \
    mel_spec_mode_cnt, \
    mel_spec_min, \
    mel_spec_max, \
    mel_spec_range, \
    mel_spec_var, \
    mel_spec_std, \
    mel_spec_first_quart, \
    mel_spec_third_quart, \
    mel_spec_inter_quart_range, \
    mel_spec_entropy, \
    mel_spec_kurt, \
    mel_spec_skew = extract_spectogam_stats(mel_spec)

    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    mel_spec_db_mean, \
    mel_spec_db_median, \
    mel_spec_db_mode, \
    mel_spec_db_mode_cnt, \
    mel_spec_db_min, \
    mel_spec_db_max, \
    mel_spec_db_range, \
    mel_spec_db_var, \
    mel_spec_db_std, \
    mel_spec_db_first_quart, \
    mel_spec_db_third_quart, \
    mel_spec_db_inter_quart_range, \
    mel_spec_db_entropy, \
    mel_spec_db_kurt, \
    mel_spec_db_skew = extract_spectogam_stats(mel_spec_db)

    mfcc = librosa.feature.mfcc(
        y=x_signals, 
        sr=hertz, 
        n_fft=samples_per_win_size, 
        hop_length=samples_per_hop_size, n_mfcc=90
    )[:, :n_frames]
    mfcc_mean, \
    mfcc_median, \
    mfcc_mode, \
    mfcc_mode_cnt, \
    mfcc_min, \
    mfcc_max, \
    mfcc_range, \
    mfcc_var, \
    mfcc_std, \
    mfcc_first_quart, \
    mfcc_third_quart, \
    mfcc_inter_quart_range, \
    mfcc_entropy, \
    mfcc_kurt, \
    mfcc_skew = extract_spectogam_stats(mfcc)
    
    spec_cont = librosa.feature.spectral_contrast(
        y=x_signals, 
        sr=hertz, 
        n_fft=samples_per_win_size, 
        hop_length=samples_per_hop_size
    )[:, :n_frames]
    spec_cont_mean, \
    spec_cont_median, \
    spec_cont_mode, \
    spec_cont_mode_cnt, \
    spec_cont_min, \
    spec_cont_max, \
    spec_cont_range, \
    spec_cont_var, \
    spec_cont_std, \
    spec_cont_first_quart, \
    spec_cont_third_quart, \
    spec_cont_inter_quart_range, \
    spec_cont_entropy, \
    spec_cont_kurt, \
    spec_cont_skew = extract_spectogam_stats(spec_cont)

    spec_cent = librosa.feature.spectral_centroid(
        y=x_signals, 
        sr=hertz, 
        n_fft=samples_per_win_size, 
        hop_length=samples_per_hop_size
    )[:, :n_frames]
    spec_bw = librosa.feature.spectral_bandwidth(
        y=x_signals, 
        sr=hertz, 
        n_fft=samples_per_win_size, 
        hop_length=samples_per_hop_size
    )[:, :n_frames]
    spec_flat = librosa.feature.spectral_flatness(
        y=x_signals, 
        n_fft=samples_per_win_size, 
        hop_length=samples_per_hop_size
    )[:, :n_frames]
    spec_roll = librosa.feature.spectral_rolloff(
        y=x_signals, 
        sr=hertz, 
        n_fft=samples_per_win_size, 
        hop_length=samples_per_hop_size
    )[:, :n_frames]

    # add the newly computed spectographic and chromagraphic
    # features as columns
    subject_features = subject_features.append_column("zcr", [zcr.reshape(-1)])
    subject_features = subject_features.append_column("poly_feat_1", [poly_feats[0, :]])
    subject_features = subject_features.append_column("poly_feat_2", [poly_feats[1, :]])
    subject_features = subject_features.append_column("spec_cent", [spec_cent.reshape(-1)])
    subject_features = subject_features.append_column("spec_bw", [spec_bw.reshape(-1)])
    subject_features = subject_features.append_column("spec_flat", [spec_flat.reshape(-1)])
    subject_features = subject_features.append_column("spec_roll", [spec_roll.reshape(-1)])

    subject_features = subject_features.append_column("mel_spec_mean", [mel_spec_mean])
    subject_features = subject_features.append_column("mel_spec_median", [mel_spec_median])
    subject_features = subject_features.append_column("mel_spec_mode", [mel_spec_mode])
    subject_features = subject_features.append_column("mel_spec_mode_cnt", [mel_spec_mode_cnt])
    subject_features = subject_features.append_column("mel_spec_min", [mel_spec_min])
    subject_features = subject_features.append_column("mel_spec_max", [mel_spec_max])
    subject_features = subject_features.append_column("mel_spec_range", [mel_spec_range])
    subject_features = subject_features.append_column("mel_spec_var", [mel_spec_var])
    subject_features = subject_features.append_column("mel_spec_std", [mel_spec_std])
    subject_features = subject_features.append_column("mel_spec_first_quart", [mel_spec_first_quart])
    subject_features = subject_features.append_column("mel_spec_third_quart", [mel_spec_third_quart])
    subject_features = subject_features.append_column("mel_spec_inter_quart_range", [mel_spec_inter_quart_range])
    subject_features = subject_features.append_column("mel_spec_entropy", [mel_spec_entropy])
    subject_features = subject_features.append_column("mel_spec_kurt", [mel_spec_kurt])
    subject_features = subject_features.append_column("mel_spec_skew", [mel_spec_skew])

    subject_features = subject_features.append_column("mel_spec_db_mean", [mel_spec_db_mean])
    subject_features = subject_features.append_column("mel_spec_db_median", [mel_spec_db_median])
    subject_features = subject_features.append_column("mel_spec_db_mode", [mel_spec_db_mode])
    subject_features = subject_features.append_column("mel_spec_db_mode_cnt", [mel_spec_db_mode_cnt])
    subject_features = subject_features.append_column("mel_spec_db_min", [mel_spec_db_min])
    subject_features = subject_features.append_column("mel_spec_db_max", [mel_spec_db_max])
    subject_features = subject_features.append_column("mel_spec_db_range", [mel_spec_db_range])
    subject_features = subject_features.append_column("mel_spec_db_var", [mel_spec_db_var])
    subject_features = subject_features.append_column("mel_spec_db_std", [mel_spec_db_std])
    subject_features = subject_features.append_column("mel_spec_db_first_quart", [mel_spec_db_first_quart])
    subject_features = subject_features.append_column("mel_spec_db_third_quart", [mel_spec_db_third_quart])
    subject_features = subject_features.append_column("mel_spec_db_inter_quart_range", [mel_spec_db_inter_quart_range])
    subject_features = subject_features.append_column("mel_spec_db_entropy", [mel_spec_db_entropy])
    subject_features = subject_features.append_column("mel_spec_db_kurt", [mel_spec_db_kurt])
    subject_features = subject_features.append_column("mel_spec_db_skew", [mel_spec_db_skew])

    subject_features = subject_features.append_column("mfcc_mean", [mfcc_mean])
    subject_features = subject_features.append_column("mfcc_median", [mfcc_median])
    subject_features = subject_features.append_column("mfcc_mode", [mfcc_mode])
    subject_features = subject_features.append_column("mfcc_mode_cnt", [mfcc_mode_cnt])
    subject_features = subject_features.append_column("mfcc_min", [mfcc_min])
    subject_features = subject_features.append_column("mfcc_max", [mfcc_max])
    subject_features = subject_features.append_column("mfcc_range", [mfcc_range])
    subject_features = subject_features.append_column("mfcc_var", [mfcc_var])
    subject_features = subject_features.append_column("mfcc_std", [mfcc_std])
    subject_features = subject_features.append_column("mfcc_first_quart", [mfcc_first_quart])
    subject_features = subject_features.append_column("mfcc_third_quart", [mfcc_third_quart])
    subject_features = subject_features.append_column("mfcc_inter_quart_range", [mfcc_inter_quart_range])
    subject_features = subject_features.append_column("mfcc_entropy", [mfcc_entropy])
    subject_features = subject_features.append_column("mfcc_kurt", [mfcc_kurt])
    subject_features = subject_features.append_column("mfcc_skew", [mfcc_skew])

    subject_features = subject_features.append_column("spec_cont_mean", [spec_cont_mean])
    subject_features = subject_features.append_column("spec_cont_median", [spec_cont_median])
    subject_features = subject_features.append_column("spec_cont_mode", [spec_cont_mode])
    subject_features = subject_features.append_column("spec_cont_mode_cnt", [spec_cont_mode_cnt])
    subject_features = subject_features.append_column("spec_cont_min", [spec_cont_min])
    subject_features = subject_features.append_column("spec_cont_max", [spec_cont_max])
    subject_features = subject_features.append_column("spec_cont_range", [spec_cont_range])
    subject_features = subject_features.append_column("spec_cont_var", [spec_cont_var])
    subject_features = subject_features.append_column("spec_cont_std", [spec_cont_std])
    subject_features = subject_features.append_column("spec_cont_first_quart", [spec_cont_first_quart])
    subject_features = subject_features.append_column("spec_cont_third_quart", [spec_cont_third_quart])
    subject_features = subject_features.append_column("spec_cont_inter_quart_range", [spec_cont_inter_quart_range])
    subject_features = subject_features.append_column("spec_cont_entropy", [spec_cont_entropy])
    subject_features = subject_features.append_column("spec_cont_kurt", [spec_cont_kurt])
    subject_features = subject_features.append_column("spec_cont_skew", [spec_cont_skew])

    return subject_features


class AudioMetaData(BaseModel):
    subject_id: str


@app.post("/predict/")
async def predict(
    audios: list[UploadFile], 
    subject_id: str=Body("X", embed=True)
):
    """
    takes as input from request the raw .wav/.flac files
    containing recordings of an individual, which is then
    converted into features normalized and then feature
    reduced. 
    
    Note parameter name in request should strictly
    be the same as the parameter name defined in the function
    here
    """

    # print(audios)
    # print(subject_id)
    # print(models)

    # connect to in memory db
    conn = duckdb.connect()

    # some default hyperparams during windowing 
    hertz = 16000 
    window_time = 3 
    hop_time = 1

    # we calculate the window size of each segment or the
    # amount of samples it has to have based on the frequency
    samples_per_win_size = int(window_time * hertz)
    samples_per_hop_size = int(hop_time * hertz)

    # read audio recordings sent by user
    ys = []
    for index, wav in enumerate(audios):
        # Download the file content
        content = await wav.read()
        audio_buff = io.BytesIO(content)

        # # local
        # audio_buff = os.path.join(wavs_dir, wav)

        # let librosa read the audio buffer containing t+he content
        # of the binary audio file
        y, sr = librosa.load(audio_buff, sr=16000)

        # audio recordings can have different length
        print(f"shape of audio signals {y.shape}")
        print(f"sampling rate of audio signals after interpolation: {sr}")

        # top_db is set to 20 representing any signal below
        # 20 decibels will be considered silence
        y_trimmed, _ = librosa.effects.trim(y, top_db=20)

    #     # append y to ys 
        ys.append(y_trimmed)

    # concatenate all audio signals into one final signal as 
    # this is all anyway recorded in the voice of the same gender
    final = np.concatenate(ys, axis=0)

    # create pyarrow table so we can write this table as
    # parquet file format later
    subject_table = pa.table({
        "signals": pa.array(final), 
        "subjectId": pa.array([subject_id] * final.shape[0], type=pa.string()),
        "rowId": pa.array(np.arange(final.shape[0]), type=pa.int32())
    })

    x_signals = subject_table["signals"].to_numpy()

    # calculate statistical features
    subject_features = compute_statistical_feats(
        conn,
        subject_table, 
        samples_per_win_size, 
        samples_per_hop_size
    )

    # get the number of frames used using a window of 48000
    # and hop length of 16000
    n_frames = subject_features.shape[0]

    # compute spectographic and chromagraphic features
    subject_features_final = compute_spectral_features(
        subject_features, 
        x_signals, 
        hertz, 
        samples_per_win_size, 
        samples_per_hop_size, 
        n_frames
    )

    # IMPUTATION
    feat_cols = [field.name for field in subject_features_final.schema if not "subjectId" in field.name]

    query = """
        CREATE OR REPLACE TEMPORARY TABLE features_imp AS (SELECT
            subjectId,
    """

    n_features = len(feat_cols)
    for i, feat_col in enumerate(feat_cols):
        if i == (n_features - 1): 
            query += f"""
                COALESCE({feat_col}, AVG({feat_col}) OVER(PARTITION BY subjectId)) AS {feat_col}_imp
            """
            break
        query += f"""
            COALESCE({feat_col}, AVG({feat_col}) OVER(PARTITION BY subjectId)) AS {feat_col}_imp,
        """
    
    query += """
        FROM subject_features_final)
    """

    conn.sql(query)
    
    test_df = conn.sql("SELECT * FROM features_imp").to_df()
    print(test_df.columns)

    # REMOVAL OF COLUMNS
    query = """
        SELECT
    """

    n_features = len(feat_cols)
    for i, feat_col in enumerate(feat_cols):
        if i == (n_features - 1): 
            query += f"""
                SUM(CAST(ISINF({feat_col}_imp) AS INTEGER)) AS {feat_col}_imp
            """
            break
        query += f"""
            SUM(CAST(ISINF({feat_col}_imp) AS INTEGER)) AS {feat_col}_imp,
        """

    query += """
        FROM features_imp
    """

    inf_cnts = conn.sql(query).fetchdf()

    def identify_inf_cols_to_remove(df, threshold=5):
        """
        it is assumed that df is single row and multidimensional 
        or with multiple columns
        """
        to_remove = []
        for column in df.columns:
            inf_cnt = int(inf_cnts[column].to_list()[-1])
            if inf_cnt > threshold:
                print(f"column {column}: {inf_cnt}")
                to_remove.append(column)

        return to_remove
    
    cols_to_remove = identify_inf_cols_to_remove(inf_cnts)
    print(cols_to_remove)

    # if no columns will be removed just skip this 
    # block all together
    if len(cols_to_remove) > 0:
        query_part = "\n".join([f"DROP COLUMN {col_to_remove}" for col_to_remove in cols_to_remove])
        query = f"""
            ALTER TABLE features_imp 
            {query_part}
        """

        conn.sql(query)

    # retrieve all data as dataframe
    subject_features_imp = conn.sql("SELECT * EXCLUDE(subjectId) FROM features_imp;").to_df()
    print(len(subject_features_imp.columns))

    # NORMALIZATION
    scaler = models["signal-gender-predictor"]["scaler"]
    subject_features_imp_sc = scaler.transform(subject_features_imp)
    subject_features_imp_sc_table = pa.table({
        feat_col: pa.array(subject_features_imp_sc[:, i]) 
        for i, feat_col in enumerate(subject_features_imp.columns)
    })

    # FEATURE SELECTION
    selected_feats = models["signal-gender-predictor"]["selected_feats"]
    subject_features_imp_sc_red_table = subject_features_imp_sc_table.select(selected_feats)
    subject_features_imp_sc_red = subject_features_imp_sc_red_table.to_pydict()

    # PREDICTION
    signal_gender_predictor = models["signal-gender-predictor"]["model"]
    preds = signal_gender_predictor.predict(subject_features_imp_sc_red)
    decoded = {"predictions": ["female" if pred else "male" for pred in (preds >= 0.5).tolist()]}

    # recall that for males the value is 0 and for 
    # females the value is 1. So if the probability value
    # is < 0.5 then it is male and if >= 0.5 it is female
    return decoded


@app.get("/")
def index():
    print(models)
    return {"Hello": "World"}