"""
physengine.mechanics.pulley
===========================

Pulley & Connected mass dynamics for Class 9 & 11 Physics.

Features:
- Standard Atwood Machine:
    a = (m1 - m2) / (m1 + m2) * g
    T = (2 * m1 * m2) / (m1 + m2) * g
- Table Pulley (horizontal sliding block + vertical hanging mass):
    a = (m_hanging - μ * m_table) / (m_hanging + m_table) * g
- Incline Pulley systems
"""

from __future__ import annotations

from physengine.math.constants import STANDARD_GRAVITY


class AtwoodMachine:
    """Standard 2-mass symmetrical Atwood machine with ideal string & pulley.

    Formulas:
        Acceleration: a = (m1 - m2) / (m1 + m2) * g
        Tension in string: T = (2 * m1 * m2) / (m1 + m2) * g
    """

    def __init__(
        self,
        m1: float,
        m2: float,
        g: float = STANDARD_GRAVITY,
    ) -> None:
        self.m1 = m1
        self.m2 = m2
        self.g = g

    @property
    def acceleration(self) -> float:
        """Magnitude of acceleration for both masses."""
        total_m = self.m1 + self.m2
        if total_m < 1e-15:
            return 0.0
        return abs(self.m1 - self.m2) / total_m * self.g

    @property
    def tension(self) -> float:
        """Tension in the connecting string."""
        total_m = self.m1 + self.m2
        if total_m < 1e-15:
            return 0.0
        return (2.0 * self.m1 * self.m2) / total_m * self.g

    def position_at(self, t: float) -> tuple[float, float]:
        """Displacements of (mass1, mass2) from initial positions at time t.

        Assuming m1 > m2 (m1 descends, m2 ascends).
        """
        a = self.acceleration
        s = 0.5 * a * t * t
        if self.m1 >= self.m2:
            return -s, s
        return s, -s


class TablePulleySystem:
    """A block on a horizontal table connected via pulley to a hanging mass.

    Formulas:
        Net driving force = m_hang * g - f_friction = (m_hang - μ_k * m_table) * g
        Acceleration: a = max(0, (m_hang - μ_k * m_table) / (m_hang + m_table) * g)
        Tension: T = m_hang * (g - a)
    """

    def __init__(
        self,
        mass_table: float,
        mass_hanging: float,
        friction_mu: float = 0.0,
        g: float = STANDARD_GRAVITY,
    ) -> None:
        self.m_table = mass_table
        self.m_hang = mass_hanging
        self.mu = friction_mu
        self.g = g

    @property
    def acceleration(self) -> float:
        """Linear acceleration of both blocks."""
        net_driving_mass = self.m_hang - self.mu * self.m_table
        if net_driving_mass <= 0:
            return 0.0
        total_m = self.m_table + self.m_hang
        return (net_driving_mass / total_m) * self.g

    @property
    def tension(self) -> float:
        """Tension in the connecting string."""
        a = self.acceleration
        return self.m_hang * (self.g - a)
