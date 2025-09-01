import requests
import zipfile
import tarfile
import os
import librosa
import numpy as np
import pandas as pd
import re
import pickle
import json
import io

from concurrent.futures import ThreadPoolExecutor


def charge_raw_data(datum: list | tuple, hertz: int, window_time: int, hop_time: int):
    """
    convert audio signals of each subject into 3D matrices to be fed
    later to an LSTM model
    """
    
    # unpack datum which is a tuple consisting of the subject
    # name, his/her audio signals represented as a vector
    # and the label or gender of the subject
    subject_name = datum[0]
    x_signals = datum[1]
    label = datum[3]

    print(subject_name)

    # get number of rows of 16000hz signals 
    n_rows = x_signals.shape[0]
    # print(n_rows)

    # we calculate the window size of each segment or the
    # amount of samples it has to have based on the frequency
    samples_per_win_size = int(window_time * hertz)
    samples_per_hop_size = int(hop_time * hertz)
    print(f"samples per window size: {samples_per_win_size}")
    print(f"samples per hop size: {samples_per_hop_size}\n")

    # initialize segments to empty list as this will store our
    # segmented signals 
    # subject_names = []
    segments = []
    labels = []

    # fig = plt.figure(figsize=(17, 5))
    n_frames = 0
    
    # this segments our signals into overlapping segments
    for i in range(0, (n_rows - samples_per_win_size) + samples_per_hop_size, samples_per_hop_size):
        # # last segment would have start x: 464000 - end x: 512000
        # # and because 512000 plus our hop size of 16000 = 528000 
        # # already exceeding 521216 this then terminates the loop
        # i += samples_per_hop_size
        # start = i
        # end = i + samples_per_win_size
        start = i
        end = min((i + samples_per_win_size), n_rows)
        # print(f'start x: {start} - end x: {end}')

        # extract segment from calculated start and end
        # indeces
        segment = x_signals[start:end]
        if segment.shape[0] < samples_per_win_size:
            last_sample = segment[-1]

            # (n_padding_we_want_for_the_front_of_the_array, 
            # n_padding_we_want_for_the_back_of_the_array)
            # 
            n_pad_to_add = samples_per_win_size - segment.shape[0]
            print(f"n padding to be added: {n_pad_to_add}") 

            # we use the last value of the segment as padding to fill in
            # the empty spots
            segment = np.pad(segment, (0, n_pad_to_add), mode="constant", constant_values=last_sample)
        
        segments.append(segment)
        labels.append(label)

    # because x_window_list and y_window_list when converted to a numpy array will
    # be of dimensions (m, 640) and (m,) respectively we need to first and foremost
    # reshpae x_window_list into a 3D matrix such that it is able to be taken in
    # by an LSTM layer, m being the number of examples, 640 being the number of time steps
    # and 1 being the number of features which will be just our raw audio signals.    
    X = np.array(segments)
    subject_signals = np.reshape(X, (X.shape[0], X.shape[1], -1))

    Y = np.array(labels)
    subject_labels = np.reshape(Y, (Y.shape[0], -1))

    frames = range(n_frames)
    print(f"number of frames resulting from window size of {samples_per_win_size} \
    and a hop size of {samples_per_hop_size} from audio signal frequency of {hertz}: {frames}")

    time = librosa.frames_to_time(frames, hop_length=samples_per_hop_size)
    print(f"shape of time calculated from number of frames: {time.shape[0]}")

    return (subject_signals, subject_labels, time)

def concur_load_data(dataset: list, split: str="train", hertz: int=16000, window_time: int=3, hop_time: int=1, config="trad"):
    # concurrent processing
    if config == "trad":
        # define directory where to load featurse and labels
        split = split.lower()
        DIR = f"./data/_EXTRACTED_FEATURES/{split}/"

        # list all .csv features and .csv labels in directory
        names = list(set([re.sub(r"_features.csv|_labels.csv", "", file) for file in os.listdir(DIR)]))

        def helper(name):
            # read csv files
            subject_features = pd.read_csv(f"./data/_EXTRACTED_FEATURES/{split}/{name}_features.csv", index_col=0)
            subject_labels = pd.read_csv(f"./data/_EXTRACTED_FEATURES/{split}/{name}_labels.csv", index_col=0)
            
            # # scale features before saving
            # feature_columns = subject_features.columns
            # scaler = StandardScaler()
            # subject_features_normed = scaler.fit_transform(subject_features)
            # subject_features = pd.DataFrame(subject_features_normed, columns=feature_columns)

            return subject_features, subject_labels

        with ThreadPoolExecutor(max_workers=5) as exe:
            # return from this will be a list of all subjects
            # features and labels e.g. [(subject1_features.csv, subject1_labels.csv)]
            subjects_data = list(exe.map(helper, names))

            # unzip subjects data and unpack
            subjects_features, subjects_labels = zip(*subjects_data)

        return subjects_features, subjects_labels, None
    else:
        def helper(datum):
            subject_signals, subject_labels, time = charge_raw_data(datum, hertz, window_time, hop_time)

            return (subject_signals, subject_labels, time)
        
        with ThreadPoolExecutor(max_workers=5) as exe:
            # return from this will be a list of all subjects
            # features and labels e.g. [(subject1_features.csv, subject1_labels.csv)]
            subjects_data = list(exe.map(helper, dataset))

            # unzip subjects data and unpack
            subjects_signals, subjects_labels, times = zip(*subjects_data)

        print("subjects signals, labels, names and subject to id lookup loaded")
        return subjects_signals, subjects_labels, times


def load_labels(DIR, folders):
    def helper(folder):
        try:
            file_path = os.path.join(DIR, folder, "etc", "README")
            with open(file_path, "r") as file:
                lines = [line for line in file.readlines() if "gender" in line.lower()]
                file.close()

            # print(lines)

            # extract only the gender of the subject in meta data
            # print(lines[0].lower())
            string = re.sub(r"(gender)", "", lines[0].lower())
            string = re.sub(r"[:;\[\]\t\n\s]", "", string)

            if string:
                gender = string
                if gender.startswith("ma") or gender.startswith("mä"):
                    return folder, string, "male"
                elif gender.startswith("fem") or gender.startswith("wei"):
                    return folder, string, "female"
                else:
                    return folder, string, "unknown"
            
        except IndexError:
            return folder, "unknown", "unknown"
        
        except FileNotFoundError:
            return folder, "unknown", "unknown"

    with ThreadPoolExecutor(max_workers=5) as exe:
        subjects_labels = list(exe.map(helper, folders))
        
        
    return subjects_labels



def load_audio(DIR: str, folders: list, hertz=16000):
    """
    loads audio signals from each .wav file of each subject
    """

    def helper(folder):
    # for folder in folders:
        try:
            wavs_dir = os.path.join(DIR, folder, "wav")
            path_to_wavs = os.listdir(wavs_dir)

        # this is if a .wav file is not used as a directory so 
        # try flac 
        except FileNotFoundError:
            wavs_dir = os.path.join(DIR, folder, "flac")
            path_to_wavs = os.listdir(wavs_dir)

        finally:
            # create storage for list of signals to all be 
            # concatenated later
            ys = []

            # create figure, and axis
            # fig, axes = plt.subplots(nrows=len(path_to_wavs), ncols=1, figsize=(12, 30))
            
            for index, wav in enumerate(path_to_wavs):

                wav_path = os.path.join(wavs_dir, wav)
                # print(wav_path)

                # each .wav file has a sampling frequency is 16000 hertz 
                y, sr = librosa.load(wav_path, sr=hertz)

                # audio recordings can have different length
                print(f"shape of audio signals {y.shape}")
                print(f"sampling rate of audio signals after interpolation: {sr}")

                # top_db is set to 20 representing any signal below
                # 20 decibels will be considered silence
                y_trimmed, _ = librosa.effects.trim(y, top_db=20)

                # append y to ys 
                ys.append(y_trimmed)

            # concatenate all audio signals into one final signal as 
            # this is all anyway recorded in the voice of the same gender
            final = np.concatenate(ys, axis=0)
            print(f"shape of final signal: {final.shape}")
            # print(f"shape of signal: {y.shape}")
            # print(f"shape of trimmed signal: {y_trimmed.shape}")
            # print(f"sampling rate: {sr}")
            # librosa.display.waveshow(final, alpha=0.5)

            # plt.tight_layout()
            # plt.show()

            return folder, final
        
    # concurrently load .wav files and trim  each .wav files
    # audio signal and combine into one signal for each subject 
    with ThreadPoolExecutor(max_workers=5) as exe:
        signals = list(exe.map(helper, folders))
        
    return signals



def load_lookup_array(path: str):
    """
    reads a text file containing a list of all unique values
    and returns this. If no file is found a false boolean is
    returned
    """

    try:
        with open(path, 'r') as file:
            feature_set = file.read()
            feature_set = feature_set.split('\n')
            file.close()

        return feature_set
    except FileNotFoundError as e:
        print("file not found please run needed script first to produce file")
        return False

def save_lookup_array(path: str, uniques: list):
    """
    saves and writes all the unique list of values to a
    a file for later loading by load_lookup_array()
    """
    uniques = [uniques[i] + '\n' for i in range(len(uniques) - 1)] + [uniques[-1]]

    with open(path, 'w') as file:
        file.writelines(uniques)
        file.close()

def save_meta_data(path: str, meta_data: dict):
    """
    saves dictionary of meta data such as hyper 
    parameters to a .json file
    """

    with open(path, 'w') as file:
        json.dump(meta_data, file)
        file.close()

def load_meta_data(path: str):
    """
    loads the saved dictionary of meta data such as
    hyper parameters from the created .json file
    """

    with open(path, 'r') as file:
        meta_data = json.load(file)
        file.close()

    return meta_data

def save_model(model, path: str):
    """
    saves partcularly an sklearn model in a .pkl file
    for later testing
    """

    with open(path, 'wb') as file:
        pickle.dump(model, file)
        file.close()

def load_model(path: str):
    """
    loads the sklearn model, scaler, or encoder stored
    in a .pkl file for later testing and deployment
    """

    with open(path, 'rb') as file:
        model = pickle.load(file)
        file.close()

    return model