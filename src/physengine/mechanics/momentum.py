"""
physengine.mechanics.momentum
=============================

Linear momentum calculations for individual bodies and systems.

Momentum is a conserved quantity in the absence of external forces,
making it essential for collision analysis and validation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from physengine.core.entity import Entity, RigidBodyComponent
from physengine.math.vector import Vector2

if TYPE_CHECKING:
    from physengine.core.world import World


def linear_momentum(entity: Entity) -> Vector2:
    """Calculate linear momentum: p = m * v.

    Args:
        entity: Entity with a RigidBodyComponent.

    Returns:
        Momentum vector (kg⋅m/s).
    """
    rb = entity.get_component(RigidBodyComponent)
    return rb.velocity * rb.mass


def total_momentum(world: World) -> Vector2:
    """Calculate total linear momentum of all dynamic entities.

    Args:
        world: The simulation world.

    Returns:
        Total momentum vector (kg⋅m/s).
    """
    total = Vector2.zero()
    for entity in world.dynamic_entities:
        total = total + linear_momentum(entity)
    return total


def impulse(force: Vector2, dt: float) -> Vector2:
    """Calculate impulse: J = F * Δt.

    Args:
        force: Force vector (N).
        dt: Time interval (s).

    Returns:
        Impulse vector (N⋅s = kg⋅m/s).
    """
    return force * dt


def apply_impulse(entity: Entity, impulse_vec: Vector2) -> None:
    """Apply an impulse to an entity, changing its velocity.

    Δv = J / m

    Args:
        entity: Target entity.
        impulse_vec: Impulse vector (N⋅s).
    """
    rb = entity.get_component(RigidBodyComponent)
    if rb.is_static:
        return
    dv = impulse_vec * rb.inverse_mass
    rb.velocity = rb.velocity + dv


def center_of_mass(world: World) -> Vector2:
    """Calculate the center of mass of all dynamic entities.

    Args:
        world: The simulation world.

    Returns:
        Center of mass position (m).
    """
    total_mass = 0.0
    weighted_pos = Vector2.zero()

    for entity in world.dynamic_entities:
        rb = entity.get_component(RigidBodyComponent)
        m = rb.mass
        total_mass += m
        weighted_pos = weighted_pos + entity.position * m

    if total_mass < 1e-30:
        return Vector2.zero()

    return weighted_pos / total_mass


def velocity_of_center_of_mass(world: World) -> Vector2:
    """Calculate the velocity of the center of mass.

    v_cm = Σ(m_i * v_i) / Σm_i

    Args:
        world: The simulation world.

    Returns:
        Center of mass velocity (m/s).
    """
    total = total_momentum(world)
    total_mass = sum(
        e.get_component(RigidBodyComponent).mass
        for e in world.dynamic_entities
    )

    if total_mass < 1e-30:
        return Vector2.zero()

    return total / total_mass
