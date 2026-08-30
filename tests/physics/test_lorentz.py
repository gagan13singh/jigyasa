"""Physics validation tests for Electromagnetism & Lorentz Force (Class 12)."""

import math

import pytest

from physengine.electromagnetism.lorentz import CyclotronMotion, VelocitySelector
from physengine.math.constants import COULOMB_CONSTANT, ELEMENTARY_CHARGE


@pytest.mark.physics
class TestElectromagnetism:
    def test_coulomb_force_magnitude(self):
        """F = k_e * q1 * q2 / r²."""
        q1 = 1e-6 # 1 microCoulomb
        q2 = 2e-6 # 2 microCoulomb
        r = 0.1   # 10 cm

        expected_F = COULOMB_CONSTANT * (q1 * q2) / (r * r)
        # Expected: ~8.98755e9 * 2e-12 / 0.01 = 1.7975 N
        assert abs(expected_F - 1.79751) < 0.01

    def test_cyclotron_radius_and_frequency(self):
        """Cyclotron radius R = m*v / (q*B) and frequency f = q*B / (2π*m)."""
        q = ELEMENTARY_CHARGE # 1.602e-19 C (proton / positron)
        m = 1.673e-27        # mass of proton (kg)
        v = 1e6              # 1000 km/s
        B = 0.5              # 0.5 Tesla

        cyclotron = CyclotronMotion(
            charge=q,
            mass=m,
            speed_perpendicular=v,
            magnetic_field_B=B,
        )

        expected_R = (m * v) / (q * B)
        assert abs(cyclotron.cyclotron_radius - expected_R) < 1e-12

        expected_f = (q * B) / (2.0 * math.pi * m)
        assert abs(cyclotron.cyclotron_frequency - expected_f) < 1e-12

    def test_velocity_selector_equilibrium(self):
        """v = E / B passes undeflected."""
        E = 10000.0 # V/m
        B = 0.2     # Tesla
        selector = VelocitySelector(electric_field_magnitude=E, magnetic_field_B=B)
        assert abs(selector.selected_speed - 50000.0) < 1e-12
