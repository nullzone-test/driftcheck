"""Core drift monitoring engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
import numpy as np

from driftcheck.statistics.ks import KSTest
from driftcheck.statistics.psi import PSITest


@dataclass
class Alert:
    feature: str
    test: str
    p_value: float
    threshold: float
    severity: str = "warning"


@dataclass
class CheckResult:
    alerts: list[Alert] = field(default_factory=list)
    passed: bool = True
    stats: dict[str, Any] = field(default_factory=dict)


class DriftMonitor:
    """Monitor feature distributions for drift against a reference dataset."""

    def __init__(
        self,
        reference_data: str | Path | pd.DataFrame,
        tests: list | None = None,
        features: list[str] | None = None,
        alert_webhook: str | None = None,
        threshold: float = 0.05,
    ):
        self.threshold = threshold
        self.features = features
        self.alert_webhook = alert_webhook
        self.tests = tests or [KSTest(threshold=threshold), PSITest(threshold=0.1)]

        if isinstance(reference_data, pd.DataFrame):
            self._reference = reference_data
        else:
            self._reference = self._load(reference_data)

    def _load(self, path: str | Path) -> pd.DataFrame:
        path = str(path)
        if path.endswith(".parquet"):
            return pd.read_parquet(path)
        elif path.endswith(".csv"):
            return pd.read_csv(path)
        elif path.startswith("s3://"):
            from driftcheck.io.s3 import read_s3_parquet
            return read_s3_parquet(path)
        raise ValueError(f"Unsupported format: {path}")

    def check(self, current_data: pd.DataFrame) -> CheckResult:
        """Run all drift tests against current data."""
        features = self.features or list(self._reference.columns)
        result = CheckResult()

        for feature in features:
            if feature not in current_data.columns:
                continue

            ref_col = self._reference[feature].dropna()
            cur_col = current_data[feature].dropna()

            for test in self.tests:
                p_value = test.run(ref_col, cur_col)
                if p_value < test.threshold:
                    alert = Alert(
                        feature=feature,
                        test=test.name,
                        p_value=p_value,
                        threshold=test.threshold,
                    )
                    result.alerts.append(alert)
                    result.passed = False

                result.stats[f"{feature}_{test.name}"] = p_value

        if not result.passed and self.alert_webhook:
            self._send_alert(result)

        return result

    def _send_alert(self, result: CheckResult) -> None:
        import requests

        payload = {
            "text": f"🚨 Drift detected: {len(result.alerts)} alert(s)",
            "alerts": [
                {"feature": a.feature, "test": a.test, "p_value": a.p_value}
                for a in result.alerts
            ],
        }
        requests.post(self.alert_webhook, json=payload, timeout=10)
