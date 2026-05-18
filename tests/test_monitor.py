"""Tests for drift monitor."""

import numpy as np
import pandas as pd
import pytest

from driftcheck import DriftMonitor


@pytest.fixture
def reference_df():
    np.random.seed(42)
    return pd.DataFrame({
        "age": np.random.normal(35, 10, 1000),
        "income": np.random.lognormal(10.5, 0.8, 1000),
        "credit_score": np.random.normal(700, 50, 1000),
    })


class TestDriftMonitor:
    def test_no_drift(self, reference_df):
        """Same distribution should pass."""
        monitor = DriftMonitor(reference_data=reference_df)
        result = monitor.check(reference_df)
        assert result.passed

    def test_drift_detected(self, reference_df):
        """Shifted distribution should trigger alerts."""
        drifted = reference_df.copy()
        drifted["age"] = drifted["age"] + 20  # large shift

        monitor = DriftMonitor(reference_data=reference_df)
        result = monitor.check(drifted)
        assert not result.passed
        assert any(a.feature == "age" for a in result.alerts)

    def test_subset_features(self, reference_df):
        """Should only check specified features."""
        monitor = DriftMonitor(
            reference_data=reference_df,
            features=["income"],
        )
        result = monitor.check(reference_df)
        assert all(
            "income" in k for k in result.stats.keys()
        )
