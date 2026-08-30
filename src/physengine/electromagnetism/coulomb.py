"""
physengine.electromagnetism.coulomb
===================================

Electrostatics for Class 12 & JEE/NEET Physics.

Features:
- Coulomb's Law: F = 1/(4πε₀) * (q1 * q2) / r² * r̂
- Uniform Electric Field force: F = q * E
- Deflection of charged particle in uniform E-field (J.J. Thomson e/m experiment):
    y(x) = (q * E) / (2 * m * vx²) * x²
- Electric Dipole Torque: τ = p × E = p * E * sin θ
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from physengine.core.entity import Component, Entity, Transform
from physengine.math.constants import COULOMB_CONSTANT
from physengine.math.vector import Vector2
from physengine.mechanics.forces import Force

if TYPE_CHECKING:
    from physengine.core.world import World


@dataclass
class ElectricChargeComponent(Component):
    """Component giving an entity an electrostatic charge."""

    charge: float = 0.0 # Coulombs (C) (e.g. electron = -1.602e-19 C)


class CoulombForce(Force):
    """Electrostatic force between two point charges (Coulomb's Law).

    F = k_e * (q_source * q_target) / r² * r̂
    Where k_e = 1/(4πε₀) ≈ 8.98755e9 N·m²/C²
    """

    def __init__(
        self,
        source_charge: float,
        source_position: Vector2,
        k_e: float = COULOMB_CONSTANT,
        softening: float = 0.05,
    ) -> None:
        self.q_source = source_charge
        self.source_pos = source_position
        self.k_e = k_e
        self.softening = softening

    def calculate(self, entity: Entity, world: World, dt: float) -> Vector2:
        if not entity.has_component(ElectricChargeComponent):
            return Vector2.zero()

        q_target = entity.get_component(ElectricChargeComponent).charge
        pos = entity.get_component(Transform).position

        r_vec = pos - self.source_pos
        dist_sq = max(r_vec.magnitude_squared, self.softening ** 2)

        # Repulsive if charges have same sign, attractive if opposite
        magnitude = self.k_e * (self.q_source * q_target) / dist_sq
        return r_vec.normalize() * magnitude


class UniformElectricField(Force):
    """Uniform Electric Field: F = q * E."""

    def __init__(self, electric_field: Vector2) -> None:
        self.E = electric_field # N/C or V/m

    def calculate(self, entity: Entity, world: World, dt: float) -> Vector2:
        if not entity.has_component(ElectricChargeComponent):
            return Vector2.zero()

        q = entity.get_component(ElectricChargeComponent).charge
        return self.E * q


class ElectronDeflectionInEField:
    """Exact analytical trajectory for a charged particle entering a uniform transverse E-field.

    Standard Class 12 NCERT example:
        Horizontal velocity vx = v0 (constant)
        Transverse acceleration: ay = (q * E) / m
        Vertical deflection inside plates of length L:
            y = (q * E * L²) / (2 * m * v0²)
        Exit angle:
            tan θ = vy / vx = (q * E * L) / (m * v0²)
    """

    def __init__(
        self,
        charge: float,
        mass: float,
        v0: float,
        E_field: float,
        plate_length: float,
    ) -> None:
        self.q = charge
        self.m = mass
        self.v0 = v0
        self.E = E_field
        self.L = plate_length

    @property
    def time_inside_plates(self) -> float:
        """t = L / v0."""
        return self.L / self.v0

    @property
    def transverse_acceleration(self) -> float:
        """ay = (q * E) / m."""
        return (self.q * self.E) / self.m

    @property
    def exit_deflection(self) -> float:
        """Vertical deflection at plate exit."""
        t = self.time_inside_plates
        return 0.5 * self.transverse_acceleration * (t ** 2)

    @property
    def exit_velocity(self) -> Vector2:
        """Exit velocity vector (vx, vy)."""
        vy = self.transverse_acceleration * self.time_inside_plates
        return Vector2(self.v0, vy)

    @property
    def exit_angle_deg(self) -> float:
        """Exit angle relative to horizontal."""
        v = self.exit_velocity
        return math.degrees(math.atan2(v.y, v.x))
