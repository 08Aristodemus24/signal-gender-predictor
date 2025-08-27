import numpy as np
import pandas as pd
import librosa
import librosa.display
import matplotlib.pyplot as plt
import os

from concurrent.futures import ThreadPoolExecutor
from scipy.stats import kurtosis as kurt, skew, entropy, mode 
from sklearn.preprocessing import MinMaxScaler, StandardScaler

def extract_features(dataset: list, split: str="train", hertz: int=16000, window_time: int=3, hop_time: int=1, config="trad"):
    """
    extracts the features from each segment of an audio signal
    """
    
    def helper(datum):
        # we access the SCR values via raw data column
        name = datum[0]
        x_signals = datum[1]
        label = datum[3]

        print(name)

        # get number of rows of 16000hz signals 
        n_rows = x_signals.shape[0]
        # print(n_rows)

        # we calculate the window size of each segment or the
        # amount of samples it has to have based on the frequency
        samples_per_win_size = int(window_time * hertz)
        samples_per_hop_size = int(hop_time * hertz)
        # print(f"samples per window size: {samples_per_win_size}")
        # print(f"samples per hop size: {samples_per_hop_size}\n")

        # initialize segments to empty list as this will store our
        # segmented signals 
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

            # # calculate frequency domain features
            # # get the spectrogram by calculating short time fourier transform
            # spectrogram = np.abs(librosa.stft(segment))
            # # print(f"spectrogram shape: {spectrogram.shape}")

            # # Get the frequencies corresponding to the spectrogram bins
            # frequencies = librosa.fft_frequencies(sr=hertz)
            # # print(f"frequencies shape: {frequencies.shape}")

            # # Find the frequency bin with the highest average energy
            # peak_frequency_bin = np.argmax(np.mean(spectrogram, axis=1))

            # # Get the peak frequency in Hz
            # # calculate also peak frequency
            # # I think dito na gagamit ng fast fourier transform
            # # to obtain the frequency, or use some sort of function
            # # to convert the raw audio signals into a spectogram
            # peak_frequency = frequencies[peak_frequency_bin]

            # # calculate the segments fast fourier transform
            # ft = np.fft.fft(segment)

            # # the fft vector can have negative or positive values
            # # so to avoid negative values and just truly see the frequencies
            # # of each segment we use its absolute values instead 
            # magnitude = np.abs(ft)
            # mag_len = magnitude.shape[0]
            # frequency = np.linspace(0, hertz, mag_len)

            # calculate statistical features
            # because the frequency for each segment is 16000hz we can divide
            # it by 1000 to instead to get its kilo hertz alternative
            mean_freq_kHz = np.mean(segment, axis=0)
            median_freq_kHz = np.median(segment, axis=0)
            std_freq = np.std(segment, axis=0)
            mode_freq = mode(segment, axis=0)
            
            # min = np.min(segment, axis=0)

            # calculate first quantile, third quantile, interquartile range
            first_quartile_kHz = np.percentile(segment, 25) / 1000,
            third_quartile_kHz = np.percentile(segment, 75) / 1000,
            inter_quartile_range_kHz = (np.percentile(segment, 75) - np.percentile(segment, 25)) / 1000,

            # compute morphological features
            skewness = skew(segment)
            kurtosis = kurt(segment)

            # compute time domain features
            amp_env = np.max(segment, axis=0)
            rms = np.sqrt(np.sum(segment ** 2, axis=0) / samples_per_win_size)

            features = {
                # statistical features
                "mean_freq_kHz": mean_freq_kHz,
                "median_freq_kHz": median_freq_kHz,
                "std_freq": std_freq,
                "mode_freq": mode_freq[0],
                'first_quartile_kHz': first_quartile_kHz[0],
                'third_quartile_kHz': third_quartile_kHz[0],
                'inter_quartile_range_kHz': inter_quartile_range_kHz[0],

                # morphological features
                "skewness": skewness,
                "kurtosis": kurtosis,

                # time domain features
                "amp_env":amp_env,
                "rms": rms,
                
                # frequency features
                # "peak_frequency": peak_frequency,
            }
            
            segments.append(features)
            labels.append(label)
            
            n_frames += 1

        frames = range(n_frames)
        # print(f"number of frames resulting from window size of {samples_per_win_size} and a hop size of {samples_per_hop_size} from audio signal frequency of {hertz}: {frames}")

        time = librosa.frames_to_time(frames, hop_length=samples_per_hop_size)
        # print(f"shape of time calculated from number of frames: {time.shape[0]}\n")
        
        # calculate other features
        zcr = librosa.feature.zero_crossing_rate(y=x_signals, frame_length=samples_per_win_size, hop_length=samples_per_hop_size)
        mel_spect = librosa.feature.melspectrogram(y=x_signals, sr=hertz, n_fft=samples_per_win_size, hop_length=samples_per_hop_size, n_mels=90)
        mel_spect_db = librosa.power_to_db(mel_spect, ref=np.max)
        mean_mel = np.mean(mel_spect_db, axis=0)
        variance_mel = np.var(mel_spect_db, axis=0)

        spect_cent = librosa.feature.spectral_centroid(y=x_signals, sr=hertz, n_fft=samples_per_win_size, hop_length=samples_per_hop_size)
        # chroma_stft = librosa.feature.chroma_stft(y=x_signals, frame_length=samples_per_win_size, hop_length=samples_per_hop_size)
        # print(mel_spect.shape, spect_cent.shape, zcr.shape)
        # print(f"mel spectrogram shape: {mel_spect.shape}")

        # calculate the number of values we need to remove in the
        # feature vector librosa calculated for us compared to the
        # feature vectors we calculated on our own
        zcr_n_values_to_rem = np.abs(zcr.shape[1] - time.shape[0])
        mean_mel_n_values_to_rem = np.abs(mean_mel.shape[0] - time.shape[0])
        spect_cent_n_values_to_rem = np.abs(spect_cent.shape[1] - time.shape[0])

        # get slice of those in range with time only
        zcr = zcr.reshape(-1)[:-zcr_n_values_to_rem]
        mean_mel = mean_mel.reshape(-1)[:-mean_mel_n_values_to_rem]
        variance_mel = variance_mel.reshape(-1)[:-mean_mel_n_values_to_rem]
        spect_cent = spect_cent.reshape(-1)[:-spect_cent_n_values_to_rem]

        # create features dataframe
        subject_features = pd.DataFrame.from_records(segments)
        subject_features["zcr"] = zcr
        subject_features["mean_mel"] = mean_mel
        subject_features["variance_mel"] = variance_mel
        subject_features["spect_cent"] = spect_cent
        
        # create labels dataframe
        subject_labels = pd.Series(labels)

        os.makedirs(f"./data/_EXTRACTED_FEATURES/{split}", exist_ok=True)
        subject_features.to_csv(f'./data/_EXTRACTED_FEATURES/{split}/{name}_features.csv')
        subject_labels.to_csv(f'./data/_EXTRACTED_FEATURES/{split}/{name}_labels.csv')

        return (subject_features, subject_labels, name, time)

    with ThreadPoolExecutor() as exe: 
        subjects_data = list(exe.map(helper, dataset))

        # unzip subjects data and unpack
        subjects_features, subjects_labels, subjects_names, time = zip(*subjects_data)
    
    return subjects_features, subjects_labels, subjects_names, time