import numpy as np


def elementwise_scoring(R_hat, R_gt, metric):
    test_mask = ~np.isnan(R_gt)

    y_hat = R_hat[test_mask].flatten()
    y_gt = R_gt[test_mask].flatten()
    return metric(y_hat, y_gt)
