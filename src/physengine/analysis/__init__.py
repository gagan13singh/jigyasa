"""
physengine.analysis
===================

Data analysis, trajectory extraction, and scientific validation.
"""

from physengine.analysis.measurements import (
    compare_scalar_with_analytical,
    compare_trajectory_with_analytical,
    energy_drift,
    momentum_conservation,
)
from physengine.analysis.recorder import StateRecorder
from physengine.analysis.trajectory import Trajectory

__all__ = [
    "StateRecorder",
    "Trajectory",
    "compare_scalar_with_analytical",
    "compare_trajectory_with_analytical",
    "energy_drift",
    "momentum_conservation",
]
