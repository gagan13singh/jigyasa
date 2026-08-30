"""
physengine.mechanics.forces
===========================

Force abstractions and implementations for classical mechanics.

Architecture:
    Force (abstract)
    ├── UniformGravity     — Constant gravitational field (F = mg)
    ├── PointGravity       — Newtonian gravity between two bodies
    ├── Drag               — Quadratic air resistance (F = -½ρCAv²v̂)
    ├── Spring             — Hooke's law (F = -k(x - x₀))
    ├── Friction           — Static + kinetic friction
    ├── ConstantForce      — Constant force in any direction
    └── CompositeForce     — Sum of multiple forces

Forces are decoupled from entities.  A Force.calculate() receives
the entity and world, and returns a force vector — nothing more.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from physengine.core.entity import Entity, RigidBodyComponent, Transform
from physengine.math.vector import EPSILON, Vector2

if TYPE_CHECKING:
    from physengine.core.world import World


class Force(ABC):
    """Abstract base class for all forces.

    A force computes a Vector2 given the current entity state and world.
    Forces are stateless with respect to the simulation — they do not
    store accumulated values.
    """

    @abstractmethod
    def calculate(self, entity: Entity, world: World, dt: float) -> Vector2:
        """Calculate the force vector acting on *entity*.

        Args:
            entity: The entity to compute force for.
            world: The simulation world (for gravity, other entities, etc.).
            dt: Current timestep (for rate-dependent forces).

        Returns:
            Force vector in Newtons (N).
        """
        ...

    @property
    def name(self) -> str:
        """Human-readable name for debugging and display."""
        return type(self).__name__


# ===========================================================================
#  Gravity Forces
# ===========================================================================
class UniformGravity(Force):
    """Constant gravitational field: F = m * g.

    This is the standard "near-Earth" gravity where g is constant
    regardless of position.

    By default, uses the gravity vector from the World config.
    """

    def __init__(self, g: Vector2 | float | None = None) -> None:
        """
        Args:
            g: Gravity vector, or scalar magnitude (applied downward).
               If None, uses world.gravity at calculation time.
        """
        self._g: Vector2 | None = None
        if g is not None:
            if isinstance(g, (int, float)):
                self._g = Vector2(0.0, -abs(float(g)))
            else:
                self._g = g

    def calculate(self, entity: Entity, world: World, dt: float) -> Vector2:
        rb = entity.get_component(RigidBodyComponent)
        g = self._g if self._g is not None else world.gravity
        return g * rb.mass


class PointGravity(Force):
    """Newtonian gravitational attraction: F = G * m1 * m2 / r² * r̂.

    Attracts the entity toward a fixed point or another entity.
    """

    def __init__(
        self,
        source_mass: float,
        source_position: Vector2,
        G: float = 6.674_30e-11,
        softening: float = 0.1,
    ) -> None:
        """
        Args:
            source_mass: Mass of the gravitational source (kg).
            source_position: Position of the source.
            G: Gravitational constant.
            softening: Minimum distance to prevent singularity (meters).
        """
        self.source_mass = source_mass
        self.source_position = source_position
        self.G = G
        self.softening = softening

    def calculate(self, entity: Entity, world: World, dt: float) -> Vector2:
        rb = entity.get_component(RigidBodyComponent)
        transform = entity.get_component(Transform)

        direction = self.source_position - transform.position
        distance_sq = max(direction.magnitude_squared, self.softening ** 2)

        magnitude = self.G * self.source_mass * rb.mass / distance_sq
        return direction.normalize() * magnitude


# ===========================================================================
#  Drag Force
# ===========================================================================
class Drag(Force):
    """Quadratic drag (air resistance): F = -½ρCAv² * v̂.

    This models the drag force on an object moving through a fluid.
    The force opposes the direction of motion.

    Attributes:
        drag_coefficient: Dimensionless drag coefficient (C_d).
                          Typical values: sphere ≈ 0.47, flat plate ≈ 1.28.
        cross_section_area: Reference area in m².
        fluid_density: Fluid density in kg/m³ (defaults to air at STP).
    """

    def __init__(
        self,
        drag_coefficient: float = 0.47,
        cross_section_area: float = 0.01,
        fluid_density: float | None = None,
    ) -> None:
        self.drag_coefficient = drag_coefficient
        self.cross_section_area = cross_section_area
        self._fluid_density = fluid_density

    def calculate(self, entity: Entity, world: World, dt: float) -> Vector2:
        rb = entity.get_component(RigidBodyComponent)
        v = rb.velocity
        speed_sq = v.magnitude_squared

        if speed_sq < EPSILON:
            return Vector2.zero()

        rho = self._fluid_density if self._fluid_density is not None else world.air_density
        magnitude = 0.5 * rho * self.drag_coefficient * self.cross_section_area * speed_sq
        speed = math.sqrt(speed_sq)
        return v * (-magnitude / speed)


# ===========================================================================
#  Spring Force (Hooke's Law)
# ===========================================================================
class Spring(Force):
    """Hooke's law spring: F = -k * (x - anchor) when stretched beyond rest_length.

    Connects an entity to a fixed anchor point with a spring.
    Optionally includes a damping term: F_damp = -c * v_radial.
    """

    def __init__(
        self,
        stiffness: float,
        anchor: Vector2,
        rest_length: float = 0.0,
        damping: float = 0.0,
    ) -> None:
        """
        Args:
            stiffness: Spring constant k (N/m).
            anchor: Fixed endpoint of the spring.
            rest_length: Natural length of the spring (meters).
            damping: Damping coefficient c (N⋅s/m).
        """
        if stiffness < 0:
            raise ValueError(f"Spring stiffness must be non-negative, got {stiffness}")
        self.stiffness = stiffness
        self.anchor = anchor
        self.rest_length = rest_length
        self.damping = damping

    def calculate(self, entity: Entity, world: World, dt: float) -> Vector2:
        transform = entity.get_component(Transform)
        displacement = transform.position - self.anchor
        distance = displacement.magnitude

        if distance < EPSILON:
            return Vector2.zero()

        # Spring force: F = -k * (distance - rest_length) * direction
        stretch = distance - self.rest_length
        direction = displacement.normalize()
        spring_force = direction * (-self.stiffness * stretch)

        # Optional damping
        if self.damping > 0:
            rb = entity.get_component(RigidBodyComponent)
            # Radial velocity component
            v_radial = rb.velocity.dot(direction)
            damping_force = direction * (-self.damping * v_radial)
            spring_force = spring_force + damping_force

        return spring_force


# ===========================================================================
#  Friction Force
# ===========================================================================
class Friction(Force):
    """Surface friction (static + kinetic).

    Applies friction to an entity sliding on a surface with a given
    normal force.  Automatically handles the static/kinetic transition.

    Simplified model:
    - If speed < threshold and applied force < μ_s * N: static (zero net force)
    - Otherwise: kinetic friction F = -μ_k * N * v̂
    """

    def __init__(
        self,
        static_coefficient: float = 0.6,
        kinetic_coefficient: float = 0.4,
        normal_force: float | None = None,
    ) -> None:
        """
        Args:
            static_coefficient: Static friction coefficient (μ_s).
            kinetic_coefficient: Kinetic friction coefficient (μ_k).
            normal_force: Normal force magnitude. If None, computed from
                          entity mass and world gravity.
        """
        if static_coefficient < kinetic_coefficient:
            raise ValueError("Static friction must be ≥ kinetic friction")
        self.mu_s = static_coefficient
        self.mu_k = kinetic_coefficient
        self._normal_force = normal_force

    def calculate(self, entity: Entity, world: World, dt: float) -> Vector2:
        rb = entity.get_component(RigidBodyComponent)
        v = rb.velocity
        speed = v.magnitude

        # Compute normal force
        N = (
            self._normal_force
            if self._normal_force is not None
            else rb.mass * abs(world.gravity.y)
        )

        if N < EPSILON:
            return Vector2.zero()

        # Static friction threshold
        static_threshold = 0.01  # speed below which we consider static

        if speed < static_threshold:
            # Static friction: resist up to μ_s * N
            # For simplicity, return zero (object stays still)
            return Vector2.zero()

        # Kinetic friction
        friction_magnitude = self.mu_k * N
        friction_direction = v.normalize() * -1.0
        return friction_direction * friction_magnitude


# ===========================================================================
#  Constant Force
# ===========================================================================
class ConstantForce(Force):
    """A constant force in a fixed direction.

    Useful for:
    - Applied forces in problems ("a 10N force pushes the block...")
    - Thrust
    - Wind
    """

    def __init__(self, force: Vector2) -> None:
        self.force = force

    def calculate(self, entity: Entity, world: World, dt: float) -> Vector2:
        return self.force


# ===========================================================================
#  Composite Force
# ===========================================================================
class CompositeForce(Force):
    """Sum of multiple forces applied as one.

    Useful for bundling forces that logically belong together.
    """

    def __init__(self, *forces: Force) -> None:
        self.forces: list[Force] = list(forces)

    def add(self, force: Force) -> CompositeForce:
        """Add a force to the composite."""
        self.forces.append(force)
        return self

    def calculate(self, entity: Entity, world: World, dt: float) -> Vector2:
        total = Vector2.zero()
        for force in self.forces:
            total = total + force.calculate(entity, world, dt)
        return total

    @property
    def name(self) -> str:
        names = [f.name for f in self.forces]
        return f"Composite({', '.join(names)})"
