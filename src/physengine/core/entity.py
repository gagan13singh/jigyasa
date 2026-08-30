"""
physengine.core.entity
======================

Entity-Component architecture for physics objects.

Instead of deep inheritance hierarchies, we compose objects from
small, focused components:

    entity = Entity("ball")
    entity.add_component(Transform(Vector2(0, 10)))
    entity.add_component(RigidBodyComponent(mass=1.0))

This allows flexible composition:
    - A Ball has Transform + RigidBody + (later) CircleCollider
    - A Wall has Transform + (later) BoxCollider
    - A ChargedParticle has Transform + RigidBody + (later) ChargeComponent
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import TypeVar

from physengine.math.vector import Vector2

T = TypeVar("T", bound="Component")


# ===========================================================================
#  Component Base
# ===========================================================================
class Component:
    """Base class for all entity components.

    Components are plain data containers.  Logic operates on
    components externally (via systems / forces / solvers).
    """

    pass


# ===========================================================================
#  Transform Component
# ===========================================================================
@dataclass
class Transform(Component):
    """Spatial position and rotation of an entity.

    Attributes:
        position: 2D position in world coordinates (meters).
        rotation: Rotation angle in radians (counter-clockwise from +x).
    """

    position: Vector2 = field(default_factory=Vector2.zero)
    rotation: float = 0.0


# ===========================================================================
#  RigidBody Component
# ===========================================================================
@dataclass
class RigidBodyComponent(Component):
    """Physical properties for dynamics simulation.

    Attributes:
        mass: Mass in kilograms.  Must be positive.
        velocity: Linear velocity in m/s.
        acceleration: Linear acceleration in m/s² (set by forces each step).
        angular_velocity: Angular velocity in rad/s.
        angular_acceleration: Angular acceleration in rad/s².
        moment_of_inertia: Rotational inertia in kg⋅m².
        is_static: If True, this body does not move (infinite mass for
                   collision response). Useful for floors, walls.
        restitution: Coefficient of restitution [0, 1] for collisions.
                     0 = perfectly inelastic, 1 = perfectly elastic.
        linear_damping: Fraction of velocity retained per second (0–1).
                        Simulates simple air resistance.
    """

    mass: float = 1.0
    velocity: Vector2 = field(default_factory=Vector2.zero)
    acceleration: Vector2 = field(default_factory=Vector2.zero)
    angular_velocity: float = 0.0
    angular_acceleration: float = 0.0
    moment_of_inertia: float = 1.0
    is_static: bool = False
    restitution: float = 1.0
    linear_damping: float = 0.0

    @property
    def inverse_mass(self) -> float:
        """1/mass, or 0 if static (infinite mass)."""
        if self.is_static or self.mass <= 0:
            return 0.0
        return 1.0 / self.mass

    def __post_init__(self) -> None:
        if self.mass <= 0 and not self.is_static:
            raise ValueError(f"Mass must be positive, got {self.mass}")
        if not (0.0 <= self.restitution <= 1.0):
            raise ValueError(f"Restitution must be in [0, 1], got {self.restitution}")


# ===========================================================================
#  Material Component (for future use)
# ===========================================================================
@dataclass
class Material(Component):
    """Surface material properties.

    Attributes:
        static_friction: Static friction coefficient.
        kinetic_friction: Kinetic friction coefficient.
        restitution: Coefficient of restitution (can override RigidBody).
        density: Material density in kg/m³.
        name: Human-readable name (e.g. "steel", "rubber").
    """

    static_friction: float = 0.6
    kinetic_friction: float = 0.4
    restitution: float = 0.5
    density: float = 1000.0
    name: str = "default"


# ===========================================================================
#  Entity
# ===========================================================================
class Entity:
    """A uniquely identified game/physics object composed of Components.

    Entities are containers — they hold components but contain no logic.
    The simulation systems (forces, solvers, collision) operate on the
    components.

    Attributes:
        id: Unique identifier (auto-generated UUID).
        name: Human-readable name for debugging and lookups.
        tags: Set of string tags for filtering and grouping.
    """

    __slots__ = ("id", "name", "tags", "_components")

    def __init__(self, name: str = "") -> None:
        self.id: str = uuid.uuid4().hex[:12]
        self.name: str = name or f"entity_{self.id[:6]}"
        self.tags: set[str] = set()
        self._components: dict[type[Component], Component] = {}

    # -- Component management ------------------------------------------------
    def add_component(self, component: Component) -> Entity:
        """Attach a component to this entity.

        If a component of the same type already exists, it is replaced.

        Args:
            component: The component instance to add.

        Returns:
            self (for method chaining).
        """
        self._components[type(component)] = component
        return self

    def get_component(self, component_type: type[T]) -> T:
        """Retrieve a component by type.

        Args:
            component_type: The Component subclass to look up.

        Returns:
            The component instance.

        Raises:
            KeyError: If the entity does not have this component type.
        """
        comp = self._components.get(component_type)
        if comp is None:
            raise KeyError(
                f"Entity '{self.name}' does not have component {component_type.__name__}"
            )
        return comp  # type: ignore[return-value]

    def has_component(self, component_type: type[Component]) -> bool:
        """Check if the entity has a component of the given type."""
        return component_type in self._components

    def remove_component(self, component_type: type[Component]) -> None:
        """Remove a component by type. No-op if not present."""
        self._components.pop(component_type, None)

    @property
    def components(self) -> dict[type[Component], Component]:
        """Read-only view of all attached components."""
        return dict(self._components)

    # -- Convenience access --------------------------------------------------
    @property
    def transform(self) -> Transform:
        """Shortcut to the Transform component."""
        return self.get_component(Transform)

    @property
    def rigid_body(self) -> RigidBodyComponent:
        """Shortcut to the RigidBodyComponent."""
        return self.get_component(RigidBodyComponent)

    @property
    def position(self) -> Vector2:
        """Current position (from Transform)."""
        return self.transform.position

    @position.setter
    def position(self, value: Vector2) -> None:
        self.transform.position = value

    @property
    def velocity(self) -> Vector2:
        """Current velocity (from RigidBody)."""
        return self.rigid_body.velocity

    @velocity.setter
    def velocity(self, value: Vector2) -> None:
        self.rigid_body.velocity = value

    # -- Tags ----------------------------------------------------------------
    def add_tag(self, tag: str) -> Entity:
        """Add a tag. Returns self for chaining."""
        self.tags.add(tag)
        return self

    def has_tag(self, tag: str) -> bool:
        """Check if entity has a specific tag."""
        return tag in self.tags

    # -- Representation ------------------------------------------------------
    def __repr__(self) -> str:
        comp_names = [c.__name__ for c in self._components]
        return f"Entity(name={self.name!r}, components={comp_names})"

    def __str__(self) -> str:
        return f"Entity({self.name})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Entity):
            return self.id == other.id
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.id)
