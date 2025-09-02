import numpy as np
import pandas as pd
import librosa
import librosa.display
import matplotlib.pyplot as plt
import os

from concurrent.futures import ThreadPoolExecutor
from scipy.stats import kurtosis as kurt, skew, entropy, mode
from sklearn.preprocessing import MinMaxScaler, StandardScaler


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