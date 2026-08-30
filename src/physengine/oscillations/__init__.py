"""physengine.oscillations — SHM, Pendulums, and Damped/Driven Oscillations."""

from physengine.oscillations.damped import (
    DampedOscillator,
    DampingRegime,
    DrivenOscillator,
)
from physengine.oscillations.pendulum import (
    CompoundPendulum,
    SimplePendulum,
    TorsionalPendulum,
)
from physengine.oscillations.shm import (
    SimpleHarmonicMotion,
    parallel_spring_constant,
    series_spring_constant,
)

__all__ = [
    "CompoundPendulum",
    "DampedOscillator",
    "DampingRegime",
    "DrivenOscillator",
    "SimpleHarmonicMotion",
    "SimplePendulum",
    "TorsionalPendulum",
    "parallel_spring_constant",
    "series_spring_constant",
]
