import pickle
import numpy as np

from sklearn.base import BaseEstimator
from tqdm import tqdm


def naive_recomendation(rate_mx, k=3):
    top_films = (~np.isnan(rate_mx)).mean(axis=0)
    return np.argsort(top_films)[-k:][::-1]


class LatentFactorModel(BaseEstimator):
    def __init__(self, hidden_ndim, lambda_, mu_, max_iter=1000):
        self.hidden_ndim = hidden_ndim
        self._lambda, self._mu = lambda_, mu_
        self.max_iter = max_iter

        self.P, self.Q = None, None

    def _get_updated_user_hidden(self, X, user_idx):
        feature_mask = ~np.isnan(X[user_idx])
        n_ratings = feature_mask.sum()

        Q_sub = self.Q[feature_mask]
        A_user = Q_sub.T @ Q_sub
        d_user = Q_sub.T @ (X[user_idx, feature_mask])

        x, _, _, _ = np.linalg.lstsq(
            self._lambda * n_ratings * np.identity(self.hidden_ndim) + A_user,
            d_user,
            rcond=None
        )
        return x

    def _get_updated_item_hidden(self, X, item_idx):
        user_mask = ~np.isnan(X[:, item_idx])
        n_ratings = user_mask.sum()

        P_sub = self.P[user_mask]
        B_item = P_sub.T @ P_sub
        d_item = P_sub.T @ (X[user_mask, item_idx])

        x, _, _, _ = np.linalg.lstsq(
            self._mu * n_ratings * np.identity(self.hidden_ndim) + B_item,
            d_item,
            rcond=None
        )
        return x

    def fit(self, X, y=None):
        self.P = np.random.normal(size=X.shape[0] * self.hidden_ndim).reshape(X.shape[0], self.hidden_ndim)
        self.Q = np.random.normal(size=X.shape[1] * self.hidden_ndim).reshape(X.shape[1], self.hidden_ndim)

        ratings_mask = ~np.isnan(X)
        known_users = ratings_mask.any(axis=1)
        known_features = ratings_mask.any(axis=0)

        for it in tqdm(range(self.max_iter), desc='LFM ALS loop'):
            for i in range(X.shape[0]):
                if not known_users[i]:
                    continue
                self.P[i] = self._get_updated_user_hidden(X, i)

            for j in range(X.shape[1]):
                if not known_features[j]:
                    continue
                self.Q[j] = self._get_updated_item_hidden(X, j)

    def predict(X):
        if (self.P is None) or (self.Q is None):
            raise RuntimeError('Firstly you need to fit')
        user_idxs, item_idxs = X[:, 0], X[:, 1]

        return self.P[user_idxs] @ self.Q[item_idxs].T

    @property
    def user_hidden(self):
        return self.P

    @property
    def item_hidden(self):
        return self.Q

    def dump_hidden_stat(self, path_prefix):
        with open(path_prefix + '__lfm_P', 'wb') as output_stream:
            pickle.dump(self.P, output_stream)
        with open(path_prefix + '__lfm_Q', 'wb') as output_stream:
            pickle.dump(self.Q, output_stream)

    def load_hidden_stat(self, path_prefix):
        with open(path_prefix + '__lfm_P', 'rb') as input_stream:
            self.P = pickle.load(input_stream)
        with open(path_prefix + '__lfm_Q', 'rb') as input_stream:
            self.Q = pickle.load(input_stream)
