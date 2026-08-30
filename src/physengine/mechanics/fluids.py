"""
physengine.mechanics.fluids
===========================

Fluid mechanics & Viscous drag for Class 11 & Advanced Physics.

Features:
- Buoyant Force (Archimedes' Principle): F_b = -ρ_fluid * V_submerged * g
- Stokes' Viscous Drag (Low Reynolds number): F_drag = -6 * π * η * r * v
- Terminal velocity calculation & verification
- Apparent weight of submerged bodies
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from physengine.core.entity import Entity, RigidBodyComponent, Transform
from physengine.math.constants import STANDARD_GRAVITY
from physengine.math.vector import Vector2
from physengine.mechanics.forces import Force

if TYPE_CHECKING:
    from physengine.core.world import World


class BuoyantForce(Force):
    """Archimedes' buoyant force acting on a submerged volume.

    F_b = ρ_fluid * V_submerged * g (upwards)
    """

    def __init__(
        self,
        fluid_density: float = 1000.0, # kg/m³ (water)
        submerged_volume: float = 0.001, # m³
        fluid_surface_y: float = 0.0,
    ) -> None:
        self.fluid_density = fluid_density
        self.submerged_volume = submerged_volume
        self.fluid_surface_y = fluid_surface_y

    def calculate(self, entity: Entity, world: World, dt: float) -> Vector2:
        transform = entity.get_component(Transform)
        # Apply buoyancy only if the entity is below the fluid surface
        if transform.position.y > self.fluid_surface_y:
            return Vector2.zero()

        g_mag = abs(world.gravity.y) if world.gravity.y != 0 else STANDARD_GRAVITY
        # Upward buoyant force
        f_buoyant = self.fluid_density * self.submerged_volume * g_mag
        return Vector2(0.0, f_buoyant)


class StokesDrag(Force):
    """Stokes' law for laminar viscous drag on a spherical particle.

    F_drag = -6 * π * η * r * v

    Applicable for small particles / low Reynolds number (e.g. Millikan oil drop,
    rain droplet forming in cloud, ball falling through glycerin/honey).
    """

    def __init__(
        self,
        radius: float,
        dynamic_viscosity: float = 1.0, # Pa·s (e.g. Castor oil ≈ 0.985, Glycerin ≈ 1.41)
    ) -> None:
        self.radius = radius
        self.eta = dynamic_viscosity

    def calculate(self, entity: Entity, world: World, dt: float) -> Vector2:
        rb = entity.get_component(RigidBodyComponent)
        v = rb.velocity
        coeff = 6.0 * math.pi * self.eta * self.radius
        return v * (-coeff)


def terminal_velocity_stokes(
    particle_radius: float,
    particle_density: float,
    fluid_density: float,
    viscosity: float,
    g: float = STANDARD_GRAVITY,
) -> float:
    """Calculate exact analytical terminal velocity of a falling sphere using Stokes' law.

    Equilibrium condition: Gravity - Buoyancy - Stokes' Drag = 0
    m*g - ρ_f*V*g - 6πηrv_t = 0
    (4/3)πr³(ρ_p - ρ_f)g = 6πηrv_t

    v_t = (2 * r² * (ρ_p - ρ_f) * g) / (9 * η)

    Args:
        particle_radius: Radius of the sphere (m).
        particle_density: Density of the sphere (kg/m³).
        fluid_density: Density of surrounding fluid (kg/m³).
        viscosity: Dynamic viscosity η (Pa·s).
        g: Gravitational acceleration (m/s²).

    Returns:
        Terminal velocity magnitude (m/s).
    """
    delta_rho = particle_density - fluid_density
    return (2.0 * (particle_radius ** 2) * delta_rho * g) / (9.0 * viscosity)
