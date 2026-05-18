"""Population Stability Index for drift detection."""

from __future__ import annotations

import numpy as np


class PSITest:
    """Population Stability Index — measures distribution shift."""

    name = "psi"

    def __init__(self, threshold: float = 0.1, bins: int = 10):
        self.threshold = threshold
        self.bins = bins

    def run(self, reference: np.ndarray, current: np.ndarray) -> float:
        """Return PSI value. Higher = more drift. Returns 1-PSI as pseudo p-value."""
        ref = np.array(reference, dtype=float)
        cur = np.array(current, dtype=float)

        # Create bins from reference distribution
        breakpoints = np.linspace(
            min(ref.min(), cur.min()),
            max(ref.max(), cur.max()),
            self.bins + 1,
        )

        ref_counts = np.histogram(ref, bins=breakpoints)[0] + 1
        cur_counts = np.histogram(cur, bins=breakpoints)[0] + 1

        ref_pct = ref_counts / ref_counts.sum()
        cur_pct = cur_counts / cur_counts.sum()

        psi = np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct))

        # Convert to pseudo p-value (higher PSI = lower p-value)
        return max(0.0, 1.0 - psi * 5)
