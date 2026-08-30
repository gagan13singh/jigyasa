"""
physengine.mechanics.collisions
===============================

1D and 2D collision physics with coefficient of restitution (e).

Models:
- Elastic collisions (e = 1.0, kinetic energy conserved)
- Inelastic collisions (0 <= e < 1.0)
- Perfectly inelastic collisions (e = 0.0, bodies stick together)
- Oblique / 2D collisions between spheres with normal & tangential decomposition
- Ballistic pendulum mechanics

All calculations use strict conservation of linear momentum and impulse-momentum theorems.
"""

from __future__ import annotations

import math

from physengine.core.entity import Entity, RigidBodyComponent, Transform
from physengine.math.vector import EPSILON, Vector2


def resolve_collision_1d(
    m1: float,
    v1: float,
    m2: float,
    v2: float,
    e: float = 1.0,
) -> tuple[float, float]:
    """Calculate 1D post-collision velocities for two colliding masses.

    Using:
    1. Conservation of Linear Momentum: m1*v1 + m2*v2 = m1*v1' + m2*v2'
    2. Coefficient of Restitution: e = (v2' - v1') / (v1 - v2)

    Formula:
        v1' = (m1*v1 + m2*v2 - m2*e*(v1 - v2)) / (m1 + m2)
        v2' = (m1*v1 + m2*v2 + m1*e*(v1 - v2)) / (m1 + m2)

    Args:
        m1: Mass of body 1 (kg).
        v1: Initial velocity of body 1 (m/s).
        m2: Mass of body 2 (kg).
        v2: Initial velocity of body 2 (m/s).
        e: Coefficient of restitution (0 <= e <= 1).

    Returns:
        (v1_final, v2_final) post-collision velocities.
    """
    total_m = m1 + m2
    if total_m < 1e-15:
        return v1, v2

    v1_final = (m1 * v1 + m2 * v2 - m2 * e * (v1 - v2)) / total_m
    v2_final = (m1 * v1 + m2 * v2 + m1 * e * (v1 - v2)) / total_m
    return v1_final, v2_final


def resolve_collision_2d(
    entity1: Entity,
    entity2: Entity,
    e: float = 1.0,
) -> tuple[Vector2, Vector2]:
    """Resolve 2D oblique collision between two particle spheres.

    Decomposes velocities along the line of centers (normal) and perpendicular (tangent).
    - Normal components undergo 1D collision with restitution e.
    - Tangential components remain unchanged (smooth surfaces, no tangential friction).

    Args:
        entity1: First colliding entity.
        entity2: Second colliding entity.
        e: Coefficient of restitution.

    Returns:
        (new_v1, new_v2) updated velocity vectors.
    """
    rb1 = entity1.get_component(RigidBodyComponent)
    rb2 = entity2.get_component(RigidBodyComponent)
    t1 = entity1.get_component(Transform)
    t2 = entity2.get_component(Transform)

    # Collision normal: from entity1 to entity2
    delta_pos = t2.position - t1.position
    dist = delta_pos.magnitude
    normal = Vector2(1.0, 0.0) if dist < EPSILON else delta_pos.normalize()
    tangent = normal.perpendicular()

    # Decompose initial velocities
    v1n = rb1.velocity.dot(normal)
    v1t = rb1.velocity.dot(tangent)

    v2n = rb2.velocity.dot(normal)
    v2t = rb2.velocity.dot(tangent)

    # Objects must be moving toward each other to collide
    if v1n - v2n <= 0:
        return rb1.velocity, rb2.velocity

    # If one body is static (infinite mass)
    if rb1.is_static:
        v2n_final = -e * v2n
        new_v2 = normal * v2n_final + tangent * v2t
        rb2.velocity = new_v2
        return rb1.velocity, new_v2

    if rb2.is_static:
        v1n_final = -e * v1n
        new_v1 = normal * v1n_final + tangent * v1t
        rb1.velocity = new_v1
        return new_v1, rb2.velocity

    # Both dynamic bodies
    v1n_final, v2n_final = resolve_collision_1d(
        rb1.mass, v1n, rb2.mass, v2n, e=e
    )

    new_v1 = normal * v1n_final + tangent * v1t
    new_v2 = normal * v2n_final + tangent * v2t

    rb1.velocity = new_v1
    rb2.velocity = new_v2

    return new_v1, new_v2


class BallisticPendulum:
    """Analytical & simulation model of a ballistic pendulum.

    A bullet of mass m moving at speed v embeds into a block of mass M
    suspended by a string of length L.

    Formulas:
        1. Inelastic collision: v_combined = (m * v) / (m + M)
        2. Energy conservation after impact: (m+M)*g*h = 1/2*(m+M)*v_combined^2
           -> h = v_combined^2 / (2g)
        3. Maximum swing angle: theta_max = arccos(1 - h/L)
    """

    def __init__(
        self,
        bullet_mass: float,
        block_mass: float,
        string_length: float,
        bullet_speed: float,
        g: float = 9.80665,
    ) -> None:
        self.m = bullet_mass
        self.M = block_mass
        self.L = string_length
        self.v0 = bullet_speed
        self.g = g

    @property
    def post_collision_speed(self) -> float:
        """Speed immediately after inelastic embedding."""
        return (self.m * self.v0) / (self.m + self.M)

    @property
    def max_height(self) -> float:
        """Maximum height attained by the pendulum bob."""
        v_comb = self.post_collision_speed
        return (v_comb * v_comb) / (2.0 * self.g)

    @property
    def max_angle_deg(self) -> float:
        """Maximum swing angle in degrees."""
        h = self.max_height
        cos_val = max(-1.0, min(1.0, 1.0 - h / self.L))
        return math.degrees(math.acos(cos_val))

    @property
    def kinetic_energy_lost(self) -> float:
        """Energy dissipated as heat/deformation during impact."""
        ke_initial = 0.5 * self.m * self.v0 * self.v0
        ke_final = 0.5 * (self.m + self.M) * (self.post_collision_speed ** 2)
        return ke_initial - ke_final
