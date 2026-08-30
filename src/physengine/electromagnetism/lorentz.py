"""
physengine.electromagnetism.lorentz
===================================

Lorentz force & Magnetic fields for Class 12 & Advanced Physics.

Features:
- Lorentz Force equation:
    F = q * (E + v × B)
- 2D/3D Magnetic Deflection:
    In 2D plane with B-field perpendicular (out of / into page):
    F_mag = q * (v_y * B * î - v_x * B * ĵ)
- Cyclotron Motion analytics:
    Radius: R = (m * v_perp) / (|q| * B)
    Time period: T = (2π * m) / (|q| * B)
    Cyclotron frequency: f = (|q| * B) / (2π * m)
- Velocity Selector:
    Equilibrium undeflected condition: v = E / B
- Helical Motion pitch:
    p = v_parallel * T
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from physengine.core.entity import Entity, RigidBodyComponent
from physengine.electromagnetism.coulomb import ElectricChargeComponent
from physengine.math.vector import Vector2
from physengine.mechanics.forces import Force

if TYPE_CHECKING:
    from physengine.core.world import World


class UniformLorentzForce(Force):
    """Combined Electric and Magnetic Lorentz force: F = q * (E + v × B).

    For 2D simulations, the magnetic field B is assumed perpendicular to the xy-plane (B_z).
    v × B = (vx*i + vy*j) × (Bz*k) = -vx*Bz*j + vy*Bz*i = (vy*Bz, -vx*Bz).
    """

    def __init__(
        self,
        electric_field: Vector2 | None = None,
        magnetic_field_z: float = 1.0, # Tesla (T)
    ) -> None:
        self.E = electric_field if electric_field is not None else Vector2.zero()
        self.Bz = magnetic_field_z

    def calculate(self, entity: Entity, world: World, dt: float) -> Vector2:
        if not entity.has_component(ElectricChargeComponent):
            return Vector2.zero()

        q = entity.get_component(ElectricChargeComponent).charge
        rb = entity.get_component(RigidBodyComponent)
        v = rb.velocity

        # Electric force: F_e = q * E
        f_electric = self.E * q

        # Magnetic force: F_m = q * (v_y * Bz, -v_x * Bz)
        f_magnetic = Vector2(v.y * self.Bz, -v.x * self.Bz) * q

        return f_electric + f_magnetic


class CyclotronMotion:
    """Exact analytical cyclotron circular and helical trajectory."""

    def __init__(
        self,
        charge: float,
        mass: float,
        speed_perpendicular: float,
        magnetic_field_B: float,
        speed_parallel: float = 0.0,
    ) -> None:
        self.q = charge
        self.m = mass
        self.v_perp = speed_perpendicular
        self.v_par = speed_parallel
        self.B = magnetic_field_B

    @property
    def cyclotron_radius(self) -> float:
        """Larmor / Cyclotron Radius: R = (m * v_perp) / (|q| * B)."""
        q_mag = abs(self.q)
        if q_mag < 1e-30 or self.B == 0:
            return float("inf")
        return (self.m * self.v_perp) / (q_mag * self.B)

    @property
    def cyclotron_frequency(self) -> float:
        """Cyclotron frequency: f = (|q| * B) / (2π * m) (independent of speed!)."""
        return (abs(self.q) * self.B) / (2.0 * math.pi * self.m)

    @property
    def time_period(self) -> float:
        """Period of 1 full circle: T = (2π * m) / (|q| * B)."""
        f = self.cyclotron_frequency
        return 1.0 / f if f > 0 else float("inf")

    @property
    def helical_pitch(self) -> float:
        """Pitch of the helix: p = v_parallel * T."""
        return self.v_par * self.time_period


class VelocitySelector:
    """Crossed Electric and Magnetic fields (E ⟂ B) filter for particles of speed v = E/B."""

    def __init__(self, electric_field_magnitude: float, magnetic_field_B: float) -> None:
        self.E = electric_field_magnitude
        self.B = magnetic_field_B

    @property
    def selected_speed(self) -> float:
        """Speed that passes undeflected: v = E / B."""
        if self.B == 0:
            return 0.0
        return self.E / self.B
