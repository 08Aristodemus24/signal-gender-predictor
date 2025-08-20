import os
import librosa
import io
import pyspark
import pyspark.sql.functions as F

from pyspark.sql import SparkSession, Window
from pyspark.conf import SparkConf
# from pyspark.context import SparkContext
from pyspark.sql.types import StringType, ArrayType, StructField, StructType, FloatType, DoubleType, IntegerType

from concurrent.futures import ThreadPoolExecutor

# Define a UDF to load audio with librosa
@F.udf(returnType=ArrayType(FloatType()))
def load_audio_with_librosa(content):
    if content is None:
        return None

    try:
        # Create a file-like object from the binary content 
        # which spark.read.format("binaryFile").load("<path>")
        # returns
        audio_buffer = io.BytesIO(content)

        # we convert this audio buffer array as audio using librosa
        # sr=None to preserve original sample rate
        y, sr = librosa.load(audio_buffer, sr=16000) 
        
        # top_db is set to 20 representing any signal below
        # 20 decibels will be considered silence
        y_trimmed, _ = librosa.effects.trim(y, top_db=20)

        # Convert numpy array to list for Spark dataframe
        return y_trimmed.tolist()
    
    except Exception as e:
        print(f"Error processing audio: {e}")
        return None
    
def load_audio(session: SparkSession, DIR: str, folders: list, hertz=16000):
    """
    loads audio signals from each .wav file of each subject
    """

    def helper(folder):
        """
        collects all the paths of wav files of each subject and
        forms a wildcard out of it that a spark session can use
        to concurrent read the files into a spark dataframe 
        """
        
        # for folder in folders:
        try:
            subject_wav_paths = os.path.join(DIR, folder, "wav", "*.wav")

        # this is if a .wav file is not used as a directory so 
        # try flac 
        except FileNotFoundError:
            subject_wav_paths = os.path.join(DIR, folder, "flac", "*.flac")

        finally:
            signal_df = session.read.format("binaryFile").load(subject_wav_paths)
            signal_df = signal_df.drop(*["modificationTime", "length"])
            signal_df = signal_df.withColumn(
                "subjectId",
                F.element_at(
                    # splits the filepath from 'file:///c:/Users/LARRY/Documents/Scripts/.../bronze/1337ad-20170321-ajg/etc/README
                    # to array of the directory tree of the files path e.g. 
                    # ['file:', ..., 'Scripts', ..., 'bronze', '<subject id>, 'etc', 'readme']
                    # so in order to extract subject id or the file name we have to 
                    # get the 3rd to the last element
                    F.split(
                        F.col("path"),
                        r"\/"
                    ),
                    -3
                )
            )
            # we convert the binary data to signals using librosa 
            signal_df = signal_df.withColumn("signals", load_audio_with_librosa("content"))

            # because the current subjects signals are segmented into parts
            # we need to group the signals list column using a collect_list() 
            # aggregator and then flatten this list of lists resulting from
            # this aggregator using flatten() 
            signal_df = signal_df.groupBy("subjectId").agg(
                # group according to subject id because we are grouping
                # a list column we will use collect list which will 
                # result in unflattened lists of lists that's why we need
                # a secondary flatten function 
                F.flatten(F.collect_list(F.col("signals"))).alias("signals")
            )

            # because the signal_df already has its signals column
            # into one single list of one row we need to "explode" this
            # value into 1 column itself
            # +--------------------+------------+
            # |           subjectId|     signals|
            # +--------------------+------------+
            # |Anniepoo-20140308...|0.0050354004|
            # |Anniepoo-20140308...|0.0042419434|
            # |Anniepoo-20140308...|0.0049743652|
            # |                 ...|         ...|
            # |Anniepoo-20140308...|0.0011901855|
            # +--------------------+------------+
            signal_df = signal_df.withColumn("signals", F.explode(F.col("signals")))   

            # create an ID column so that when this is saved
            # randomly we can order the dataframe again in the 
            # next second stage transformation
            id_window = Window.orderBy(F.col("subjectId"))
            signal_df = signal_df.withColumn("ID", F.row_number().over(id_window) - 1)

            signal_df.show()

            return folder, signal_df
        
    # concurrently load .wav files and trim  each .wav files
    # audio signal and combine into one signal for each subject 
    with ThreadPoolExecutor(max_workers=5) as exe:
        signals_df = list(exe.map(helper, folders))
        
    return signals_df



def save_data_splits(df: list[tuple[str, pyspark.sql.DataFrame]] | pyspark.sql.DataFrame, split: str, type_: str, save_path: str):
    """
    saves the dataframe into different folders in a silver
    staging layer representing the train, validation, and 
    test splits

    args:
        df - a list of tuples with pairs of the subject name
        and its respective spark dataframe representing its
        signals

        split - a string that tells the function what folder
        should the data split with dataframes be saved. Can
        either be 'train', 'validate', or 'test' 

        type - a string that tells the function if the dataframe
        to be saved is the labels or the signals. Can either
        be 'labels' or 'signals'

        save_path - a string that tells this function where to
        save the dataframe
    """
    # make a directory based on the data split specified
    # e.g. train, validate, test
    os.makedirs(os.path.join(save_path, split), exist_ok=True)
    
    if type_.lower() == "signals":
        def helper(subject_signal_df):
            subject_id, signal_df = subject_signal_df
            print(f"saving {subject_id} signals...")
            file_name = f"{save_path}/{split}/{subject_id}_signals.parquet"
            signal_df.write.mode("overwrite").parquet(file_name)
        
        # loop through each subjects signal dataframe
        # concurrently
        with ThreadPoolExecutor(max_workers=5) as exe:
            exe.map(helper, df)

    elif type_.lower() == "labels":
        file_name = f"{save_path}/{split}/labels.parquet"
        df.write.mode("overwrite").parquet(file_name)