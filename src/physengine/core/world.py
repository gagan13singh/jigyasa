"""
physengine.core.world
=====================

The World is the container for all physics entities, global forces, and
environment settings.  It is the "scene" that a Simulation operates on.

The World does not advance time — that's the Simulation's job.
The World simply provides structured access to the objects within it.

Usage:
    >>> world = World(gravity=Vector2(0, -9.81))
    >>> world.add(ball)
    >>> world.add_force(drag_force)
    >>> for entity in world.entities:
    ...     print(entity.name)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from physengine.core.config import SimulationConfig
from physengine.core.entity import Entity, RigidBodyComponent
from physengine.core.events import EntityAdded, EntityRemoved, EventBus
from physengine.math.vector import Vector2

if TYPE_CHECKING:
    from physengine.mechanics.forces import Force


class World:
    """Container for all simulation objects and global forces.

    Attributes:
        config: Simulation configuration (gravity, air density, etc.).
        event_bus: Event bus for entity lifecycle events.
    """

    def __init__(
        self,
        gravity: Vector2 | float | None = None,
        config: SimulationConfig | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        """
        Args:
            gravity: Gravity vector, or a scalar (applied downward).
                     Overrides config.gravity if provided.
            config: Full simulation config. Defaults to SimulationConfig().
            event_bus: Event bus to use. Creates a new one if not provided.
        """
        self.config = config or SimulationConfig()
        self.event_bus = event_bus or EventBus()

        # Override gravity if explicitly provided
        if gravity is not None:
            if isinstance(gravity, (int, float)):
                self.config.gravity = Vector2(0.0, -abs(float(gravity)))
            elif isinstance(gravity, Vector2):
                self.config.gravity = gravity

        # Entity storage: ordered dict for deterministic iteration
        self._entities: dict[str, Entity] = {}

        # Global forces (applied to ALL dynamic entities)
        self._global_forces: list[Force] = []

        # Per-entity forces (mapped by entity ID)
        self._entity_forces: dict[str, list[Force]] = {}

    # -- Entity management ---------------------------------------------------
    def add(self, entity: Entity) -> World:
        """Add an entity to the world.

        Emits an EntityAdded event.

        Args:
            entity: The entity to add.

        Returns:
            self (for chaining).
        """
        self._entities[entity.id] = entity
        self.event_bus.emit(EntityAdded(entity_id=entity.id, entity_name=entity.name))
        return self

    def remove(self, entity: Entity) -> None:
        """Remove an entity from the world.

        Also removes any per-entity forces. Emits EntityRemoved.
        """
        if entity.id in self._entities:
            del self._entities[entity.id]
            self._entity_forces.pop(entity.id, None)
            self.event_bus.emit(EntityRemoved(entity_id=entity.id, entity_name=entity.name))

    def get_entity(self, name_or_id: str) -> Entity:
        """Look up an entity by name or ID.

        Raises:
            KeyError: If not found.
        """
        # Try by ID first
        if name_or_id in self._entities:
            return self._entities[name_or_id]
        # Search by name
        for entity in self._entities.values():
            if entity.name == name_or_id:
                return entity
        raise KeyError(f"Entity '{name_or_id}' not found in world")

    def has_entity(self, name_or_id: str) -> bool:
        """Check if an entity exists (by name or ID)."""
        try:
            self.get_entity(name_or_id)
            return True
        except KeyError:
            return False

    @property
    def entities(self) -> list[Entity]:
        """All entities in the world."""
        return list(self._entities.values())

    @property
    def dynamic_entities(self) -> list[Entity]:
        """Entities that have a RigidBody and are not static."""
        result: list[Entity] = []
        for e in self._entities.values():
            if e.has_component(RigidBodyComponent):
                rb = e.get_component(RigidBodyComponent)
                if not rb.is_static:
                    result.append(e)
        return result

    @property
    def entity_count(self) -> int:
        """Number of entities in the world."""
        return len(self._entities)

    # -- Force management ----------------------------------------------------
    def add_force(self, force: Force) -> World:
        """Add a global force (applied to all dynamic entities).

        Args:
            force: The force to add globally.

        Returns:
            self (for chaining).
        """
        self._global_forces.append(force)
        return self

    def add_force_to(self, entity: Entity, force: Force) -> World:
        """Add a force to a specific entity only.

        Args:
            entity: Target entity.
            force: The force to apply.

        Returns:
            self (for chaining).
        """
        if entity.id not in self._entity_forces:
            self._entity_forces[entity.id] = []
        self._entity_forces[entity.id].append(force)
        return self

    def get_forces_for(self, entity: Entity) -> list[Force]:
        """Get all forces acting on an entity (global + per-entity).

        Returns:
            Combined list of global and entity-specific forces.
        """
        forces: list[Force] = list(self._global_forces)
        if entity.id in self._entity_forces:
            forces.extend(self._entity_forces[entity.id])
        return forces

    @property
    def global_forces(self) -> list[Force]:
        """All global forces."""
        return list(self._global_forces)

    def clear_forces(self) -> None:
        """Remove all forces (global and per-entity)."""
        self._global_forces.clear()
        self._entity_forces.clear()

    # -- Environment ---------------------------------------------------------
    @property
    def gravity(self) -> Vector2:
        """Gravity vector from config."""
        return self.config.gravity

    @gravity.setter
    def gravity(self, value: Vector2) -> None:
        self.config.gravity = value

    @property
    def air_density(self) -> float:
        """Air density from config."""
        return self.config.air_density

    # -- Utilities -----------------------------------------------------------
    def clear(self) -> None:
        """Remove all entities and forces."""
        self._entities.clear()
        self._global_forces.clear()
        self._entity_forces.clear()

    def __repr__(self) -> str:
        return (
            f"World(entities={self.entity_count}, "
            f"forces={len(self._global_forces)}, "
            f"gravity={self.config.gravity})"
        )

    def __contains__(self, entity: Entity) -> bool:
        return entity.id in self._entities
