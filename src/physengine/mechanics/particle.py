"""
physengine.mechanics.particle
=============================

Convenience wrapper for creating particle entities.

A Particle is not a new class hierarchy — it simply creates an Entity
pre-loaded with Transform + RigidBodyComponent.  This keeps the API
friendly while using the entity-component architecture internally.

Usage:
    >>> ball = Particle(mass=1.0, position=(0, 10), velocity=(5, 0), name="ball")
    >>> world.add(ball)
    >>> ball.position          # Vector2(0, 10)
    >>> ball.kinetic_energy    # 12.5
"""

from __future__ import annotations

from physengine.core.entity import Entity, RigidBodyComponent, Transform
from physengine.math.vector import Vector2


class Particle(Entity):
    """A point-mass particle — the simplest physical object.

    Internally composed of Transform + RigidBodyComponent.
    All physics (forces, integration) operates on those components.

    This is a convenience class: you could build the same object with::

        e = Entity("ball")
        e.add_component(Transform(Vector2(0, 10)))
        e.add_component(RigidBodyComponent(mass=1, velocity=Vector2(5, 0)))

    But ``Particle(mass=1, position=(0,10), velocity=(5,0), name="ball")``
    is much nicer for users.
    """

    def __init__(
        self,
        mass: float = 1.0,
        position: Vector2 | tuple[float, float] = (0.0, 0.0),
        velocity: Vector2 | tuple[float, float] = (0.0, 0.0),
        name: str = "",
        restitution: float = 1.0,
        is_static: bool = False,
        linear_damping: float = 0.0,
    ) -> None:
        """
        Args:
            mass: Mass in kg. Must be positive (unless is_static).
            position: Initial position as Vector2 or (x, y) tuple.
            velocity: Initial velocity as Vector2 or (x, y) tuple.
            name: Human-readable name for this particle.
            restitution: Coefficient of restitution [0, 1].
            is_static: If True, particle does not move.
            linear_damping: Velocity damping fraction per second.
        """
        super().__init__(name or "particle")

        # Convert tuples to Vector2
        if isinstance(position, (tuple, list)):
            position = Vector2(float(position[0]), float(position[1]))
        if isinstance(velocity, (tuple, list)):
            velocity = Vector2(float(velocity[0]), float(velocity[1]))

        self.add_component(Transform(position=position))
        self.add_component(RigidBodyComponent(
            mass=mass,
            velocity=velocity,
            is_static=is_static,
            restitution=restitution,
            linear_damping=linear_damping,
        ))

        self.add_tag("particle")

    # -- Convenience properties ----------------------------------------------
    @property
    def mass(self) -> float:
        """Mass of the particle (kg)."""
        return self.rigid_body.mass

    @mass.setter
    def mass(self, value: float) -> None:
        self.rigid_body.mass = value

    @property
    def acceleration(self) -> Vector2:
        """Current acceleration."""
        return self.rigid_body.acceleration

    @property
    def speed(self) -> float:
        """Scalar speed (magnitude of velocity)."""
        return self.velocity.magnitude

    @property
    def kinetic_energy(self) -> float:
        """Kinetic energy: ½mv²."""
        return 0.5 * self.mass * self.velocity.magnitude_squared

    @property
    def momentum(self) -> Vector2:
        """Linear momentum: p = mv."""
        return self.velocity * self.mass

    def __repr__(self) -> str:
        return (
            f"Particle(name={self.name!r}, "
            f"mass={self.mass}, "
            f"pos={self.position}, "
            f"vel={self.velocity})"
        )


class StaticBody(Entity):
    """A static (immovable) body — useful for floors, walls, obstacles.

    Has infinite effective mass for collision response.
    """

    def __init__(
        self,
        position: Vector2 | tuple[float, float] = (0.0, 0.0),
        name: str = "",
    ) -> None:
        super().__init__(name or "static_body")

        if isinstance(position, (tuple, list)):
            position = Vector2(float(position[0]), float(position[1]))

        self.add_component(Transform(position=position))
        self.add_component(RigidBodyComponent(
            mass=1.0,
            is_static=True,
        ))

        self.add_tag("static")
