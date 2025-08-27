import numpy as np
import pandas as pd

from sklearn.preprocessing import LabelEncoder, OrdinalEncoder


def encode_features(X):
    """
    encodes the categorical features of a dataset into numerical values
    given the desired feature to encode and the input X to transform

    if shape of input is a one dimensional array and not a typical
    matrix reshape it to an m x 1 matrix instead by expanding its 
    dimensions. Usually this will be a the target column of 1 
    dimension. Otherwise use the ordinal encoder which is suitable for
    matrices like the set of independent variables of an X input

    used during training, validation, and testing/deployment (since
    encoder is saved and later used)
    """

    
    enc = LabelEncoder() if len(X.shape) < 2 else OrdinalEncoder(dtype=np.int64)
    print(enc)
    enc_feats = enc.fit_transform(X)
    return enc_feats, enc