"""driftcheck — lightweight model drift detection."""

from driftcheck.monitor import DriftMonitor
from driftcheck.statistics.ks import KSTest
from driftcheck.statistics.psi import PSITest

__version__ = "0.3.1"
__all__ = ["DriftMonitor", "KSTest", "PSITest"]
