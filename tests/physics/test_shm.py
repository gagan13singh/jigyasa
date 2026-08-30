"""Physics validation tests for SHM, Pendulums, and Damped Oscillators (Class 11)."""

import math

import pytest

from physengine.oscillations.damped import DampedOscillator, DampingRegime
from physengine.oscillations.pendulum import SimplePendulum
from physengine.oscillations.shm import (
    SimpleHarmonicMotion,
    parallel_spring_constant,
    series_spring_constant,
)


@pytest.mark.physics
class TestSHMAndPendulums:
    def test_shm_energy_conservation(self):
        """Total mechanical energy in SHM must be equal at all phases."""
        shm = SimpleHarmonicMotion(amplitude=2.0, stiffness=50.0, mass=2.0)
        # Total energy E = 1/2 * k * A² = 0.5 * 50 * 4 = 100 J
        assert abs(shm.total_energy - 100.0) < 1e-12

        # At various times, KE(t) + PE(t) = E_total
        for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
            e_sum = shm.kinetic_energy_at(t) + shm.potential_energy_at(t)
            assert abs(e_sum - shm.total_energy) < 1e-12

    def test_spring_combinations(self):
        """Series and Parallel equivalent spring constants."""
        k1, k2 = 100.0, 100.0
        # Parallel: k_eq = k1 + k2 = 200
        assert abs(parallel_spring_constant(k1, k2) - 200.0) < 1e-12
        # Series: 1/k_eq = 1/100 + 1/100 -> k_eq = 50
        assert abs(series_spring_constant(k1, k2) - 50.0) < 1e-12

    def test_simple_pendulum_small_angle(self):
        """T = 2π * √(L / g)."""
        L = 1.0
        g = 9.81
        pendulum = SimplePendulum(length=L, initial_angle_deg=5.0, g=g)
        expected_T = 2.0 * math.pi * math.sqrt(1.0 / 9.81)
        assert abs(pendulum.period_small_angle - expected_T) < 1e-12

    def test_damped_oscillator_regimes(self):
        """Verify underdamped and overdamped classification."""
        m, k = 1.0, 100.0 # omega_0 = 10 rad/s
        # Critical damping: gamma_c = 2*sqrt(m*k) = 20 N·s/m

        under = DampedOscillator(mass=m, stiffness=k, damping_coefficient=5.0)
        assert under.regime == DampingRegime.UNDERDAMPED

        over = DampedOscillator(mass=m, stiffness=k, damping_coefficient=30.0)
        assert over.regime == DampingRegime.OVERDAMPED
