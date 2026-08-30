"""
physengine.oscillations.pendulum
================================

Pendulum systems for Class 11 & Advanced Physics.

Features:
- Simple Pendulum (small-angle approximation and large-angle exact corrections):
    T_small = 2π * √(L / g)
    T_exact ≈ T_small * (1 + 1/16 * θ₀² + 11/3072 * θ₀⁴)
- Compound / Physical Pendulum:
    T = 2π * √(I / (m * g * d))
- Torsional Pendulum:
    T = 2π * √(I / C)
"""

from __future__ import annotations

import math

from physengine.math.constants import STANDARD_GRAVITY
from physengine.math.vector import Vector2


class SimplePendulum:
    """Exact & small-angle pendulum analytical solutions."""

    def __init__(
        self,
        length: float,
        mass: float = 1.0,
        initial_angle_deg: float = 15.0,
        g: float = STANDARD_GRAVITY,
    ) -> None:
        self.L = length
        self.m = mass
        self.theta0_deg = initial_angle_deg
        self.theta0_rad = math.radians(initial_angle_deg)
        self.g = g

        self.omega_0 = math.sqrt(g / length)

    @property
    def period_small_angle(self) -> float:
        """Standard textbook period T = 2π * √(L / g)."""
        return 2.0 * math.pi * math.sqrt(self.L / self.g)

    @property
    def period_exact_series(self) -> float:
        """High-precision Borda series expansion for large amplitude oscillations.

        T ≈ T₀ * (1 + 1/4*sin²(θ₀/2) + 9/64*sin⁴(θ₀/2))
        """
        k = math.sin(self.theta0_rad / 2.0)
        correction = 1.0 + 0.25 * (k ** 2) + (9.0 / 64.0) * (k ** 4)
        return self.period_small_angle * correction

    def angle_at(self, t: float) -> float:
        """Angular displacement θ(t) in radians (small-angle regime)."""
        return self.theta0_rad * math.cos(self.omega_0 * t)

    def angular_velocity_at(self, t: float) -> float:
        """Angular velocity ω(t) in rad/s."""
        return -self.theta0_rad * self.omega_0 * math.sin(self.omega_0 * t)

    def bob_position_at(self, t: float, anchor: Vector2 | None = None) -> Vector2:
        """Cartesian (x, y) coordinates of the bob at time t."""
        anc = anchor if anchor is not None else Vector2.zero()
        theta = self.angle_at(t)
        return Vector2(
            anc.x + self.L * math.sin(theta),
            anc.y - self.L * math.cos(theta),
        )

    def bob_velocity_at(self, t: float) -> Vector2:
        """Cartesian velocity (vx, vy) of the bob at time t."""
        theta = self.angle_at(t)
        omega = self.angular_velocity_at(t)
        return Vector2(
            self.L * omega * math.cos(theta),
            self.L * omega * math.sin(theta),
        )


class CompoundPendulum:
    """Rigid physical body oscillating about a fixed horizontal axis.

    Period: T = 2π * √(I / (m * g * d))
    Where:
        I = Moment of inertia about the suspension pivot = I_cm + m*d²
        d = Distance between pivot and center of mass
    """

    def __init__(
        self,
        mass: float,
        I_pivot: float,
        distance_to_cm: float,
        g: float = STANDARD_GRAVITY,
    ) -> None:
        self.m = mass
        self.I = I_pivot
        self.d = distance_to_cm
        self.g = g

    @property
    def period(self) -> float:
        """T = 2π * √(I / (m * g * d))."""
        denominator = self.m * self.g * self.d
        if denominator <= 0:
            return float("inf")
        return 2.0 * math.pi * math.sqrt(self.I / denominator)

    @property
    def equivalent_simple_pendulum_length(self) -> float:
        """L_eq = I / (m * d)."""
        return self.I / (self.m * self.d)


class TorsionalPendulum:
    """Torsional oscillator (wire with torsional constant C and inertia I).

    Equation of motion: I * θ'' + C * θ = 0
    Period: T = 2π * √(I / C)
    """

    def __init__(
        self,
        moment_of_inertia: float,
        torsional_constant: float, # C (N·m/rad)
    ) -> None:
        self.I = moment_of_inertia
        self.C = torsional_constant

    @property
    def period(self) -> float:
        """T = 2π * √(I / C)."""
        return 2.0 * math.pi * math.sqrt(self.I / self.C)
