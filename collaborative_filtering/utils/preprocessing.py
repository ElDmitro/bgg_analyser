import pandas as pd
import numpy as np


def rate_frame_from_ratemap(ratemap):
    records = list()
    for user, rates in ratemap.items():
        row = rates.copy()
        row['username'] = user
        records.append(row)

    return pd.DataFrame(records).set_index('username')

def get_idx_mapping(rate_frame):
    return (
        pd.DataFrame(rate_frame.index).reset_index().set_index('username'),
        pd.DataFrame(rate_frame.columns, columns=['items']).reset_index().set_index('items')
    )

def train_test_mask(X, test_size=.2):
    nan_mask = np.isnan(X)

    nonan_idxs = np.arange(X.size).reshape(X.shape)[~nan_mask]
    np.random.shuffle(nonan_idxs)

    test_idxs = nonan_idxs[:int(nonan_idxs.size * test_size)]
    test_mask = np.full((X.size,), False)
    test_mask[test_idxs] = True
    test_mask = test_mask.reshape(X.shape)

    return ~test_mask, test_mask

def train_test_split(X, test_size=.2):
    train_mask, test_mask = train_test_mask(X, test_size)

    X_train = X.copy()
    X_train[test_mask] = np.nan

    X_test = X.copy()
    X_test[train_mask] = np.nan

    return X_train, X_test
