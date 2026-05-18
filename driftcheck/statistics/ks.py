"""Kolmogorov-Smirnov two-sample test for drift detection."""

from __future__ import annotations

import numpy as np
from scipy import stats


class KSTest:
    """Two-sample KS test for continuous features."""

    name = "ks"

    def __init__(self, threshold: float = 0.05):
        self.threshold = threshold

    def run(self, reference: np.ndarray, current: np.ndarray) -> float:
        """Return p-value of KS test. Low p-value = drift detected."""
        statistic, p_value = stats.ks_2samp(reference, current)
        return p_value
