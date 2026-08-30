"""
physengine.oscillations.shm
===========================

Simple Harmonic Motion (SHM) analytics and spring combinations.

Features:
- Linear SHM analytical solution:
    x(t) = A * cos(ωt + φ)
    v(t) = -ω * A * sin(ωt + φ)
    a(t) = -ω² * x(t)
- Energy relations:
    KE(x) = ½ * m * ω² * (A² - x²)
    PE(x) = ½ * m * ω² * x²
    E_total = ½ * k * A² = constant
- Spring combinations:
    Series: 1 / k_eq = 1 / k1 + 1 / k2 + ...
    Parallel: k_eq = k1 + k2 + ...
"""

from __future__ import annotations

import math


class SimpleHarmonicMotion:
    """Exact analytical model of 1D Simple Harmonic Motion."""

    def __init__(
        self,
        amplitude: float,
        angular_frequency: float | None = None,
        stiffness: float | None = None,
        mass: float | None = None,
        phase_rad: float = 0.0,
    ) -> None:
        """
        Args:
            amplitude: Maximum displacement A (m).
            angular_frequency: omega = sqrt(k/m) (rad/s).
            stiffness: Spring constant k (N/m).
            mass: Mass m (kg).
            phase_rad: Initial phase angle phi (radians).
        """
        self.A = amplitude
        self.phi = phase_rad

        if angular_frequency is not None:
            self.omega = angular_frequency
            self.m = mass if mass is not None else 1.0
            self.k = self.m * (self.omega ** 2)
        elif stiffness is not None and mass is not None:
            if mass <= 0 or stiffness < 0:
                raise ValueError("Mass must be > 0 and stiffness >= 0")
            self.k = stiffness
            self.m = mass
            self.omega = math.sqrt(stiffness / mass)
        else:
            raise ValueError("Must provide either angular_frequency or (stiffness and mass)")

    @property
    def period(self) -> float:
        """Time period T = 2π / ω."""
        return (2.0 * math.pi) / self.omega if self.omega > 0 else float("inf")

    @property
    def frequency(self) -> float:
        """Frequency f = 1 / T = ω / 2π (Hz)."""
        return self.omega / (2.0 * math.pi)

    @property
    def total_energy(self) -> float:
        """E = ½ * k * A² = ½ * m * ω² * A²."""
        return 0.5 * self.k * (self.A ** 2)

    def position_at(self, t: float) -> float:
        """x(t) = A * cos(ωt + φ)."""
        return self.A * math.cos(self.omega * t + self.phi)

    def velocity_at(self, t: float) -> float:
        """v(t) = -A * ω * sin(ωt + φ)."""
        return -self.A * self.omega * math.sin(self.omega * t + self.phi)

    def acceleration_at(self, t: float) -> float:
        """a(t) = -ω² * x(t)."""
        return - (self.omega ** 2) * self.position_at(t)

    def kinetic_energy_at(self, t: float) -> float:
        """KE(t) = ½ * m * v(t)²."""
        v = self.velocity_at(t)
        return 0.5 * self.m * v * v

    def potential_energy_at(self, t: float) -> float:
        """PE(t) = ½ * k * x(t)²."""
        x = self.position_at(t)
        return 0.5 * self.k * x * x


# -- Spring Combination Helpers ----------------------------------------------
def series_spring_constant(*stiffnesses: float) -> float:
    """Calculate equivalent spring constant for springs in series.

    1 / k_eq = 1 / k1 + 1 / k2 + ...
    """
    if not stiffnesses:
        return 0.0
    inv_sum = sum(1.0 / k for k in stiffnesses if k > 0)
    return 1.0 / inv_sum if inv_sum > 0 else 0.0


def parallel_spring_constant(*stiffnesses: float) -> float:
    """Calculate equivalent spring constant for springs in parallel.

    k_eq = k1 + k2 + ...
    """
    return sum(stiffnesses)
