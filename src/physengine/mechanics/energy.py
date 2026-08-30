"""
physengine.mechanics.energy
===========================

Energy calculations for the classical mechanics module.

Provides functions for:
- Kinetic energy (translational)
- Gravitational potential energy
- Spring (elastic) potential energy
- Total mechanical energy (for conservation analysis)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from physengine.core.entity import Entity, RigidBodyComponent, Transform

if TYPE_CHECKING:
    from physengine.core.world import World


def kinetic_energy(entity: Entity) -> float:
    """Calculate translational kinetic energy: KE = ½mv².

    Args:
        entity: Entity with a RigidBodyComponent.

    Returns:
        Kinetic energy in Joules.
    """
    rb = entity.get_component(RigidBodyComponent)
    return 0.5 * rb.mass * rb.velocity.magnitude_squared


def gravitational_potential_energy(
    entity: Entity,
    gravity: float | None = None,
    reference_height: float = 0.0,
) -> float:
    """Calculate gravitational PE: U = m * g * (h - h_ref).

    Args:
        entity: Entity with Transform and RigidBody.
        gravity: Gravitational acceleration magnitude.
                 If None, uses 9.80665 m/s².
        reference_height: Reference height (y) for PE = 0.

    Returns:
        Gravitational potential energy in Joules.
    """
    rb = entity.get_component(RigidBodyComponent)
    transform = entity.get_component(Transform)
    g = gravity if gravity is not None else 9.80665
    h = transform.position.y - reference_height
    return rb.mass * g * h


def spring_potential_energy(
    stiffness: float,
    displacement: float,
) -> float:
    """Calculate elastic potential energy: U = ½kx².

    Args:
        stiffness: Spring constant k (N/m).
        displacement: Displacement from equilibrium (m).

    Returns:
        Elastic potential energy in Joules.
    """
    return 0.5 * stiffness * displacement * displacement


def total_kinetic_energy(world: World) -> float:
    """Calculate total kinetic energy of all dynamic entities.

    Args:
        world: The simulation world.

    Returns:
        Total kinetic energy in Joules.
    """
    total = 0.0
    for entity in world.dynamic_entities:
        total += kinetic_energy(entity)
    return total


def total_gravitational_pe(
    world: World,
    reference_height: float = 0.0,
) -> float:
    """Calculate total gravitational PE of all dynamic entities.

    Args:
        world: The simulation world.
        reference_height: Reference height for PE = 0.

    Returns:
        Total gravitational PE in Joules.
    """
    g = abs(world.gravity.y)
    total = 0.0
    for entity in world.dynamic_entities:
        total += gravitational_potential_energy(
            entity, gravity=g, reference_height=reference_height
        )
    return total


def total_mechanical_energy(
    world: World,
    reference_height: float = 0.0,
) -> float:
    """Calculate total mechanical energy (KE + gravitational PE).

    Args:
        world: The simulation world.
        reference_height: Reference height for PE = 0.

    Returns:
        Total mechanical energy in Joules.
    """
    return total_kinetic_energy(world) + total_gravitational_pe(
        world, reference_height
    )


def energy_breakdown(
    entity: Entity,
    gravity: float | None = None,
    reference_height: float = 0.0,
) -> dict[str, float]:
    """Get a breakdown of energy components for a single entity.

    Args:
        entity: The entity to analyze.
        gravity: Gravitational acceleration.
        reference_height: Reference height for PE.

    Returns:
        Dictionary with keys: "kinetic", "gravitational_pe", "total".
    """
    ke = kinetic_energy(entity)
    gpe = gravitational_potential_energy(entity, gravity, reference_height)
    return {
        "kinetic": ke,
        "gravitational_pe": gpe,
        "total": ke + gpe,
    }
