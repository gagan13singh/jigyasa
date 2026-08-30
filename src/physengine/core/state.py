"""
physengine.core.state
=====================

Immutable state snapshots for recording, replay, and analysis.

The simulation loop captures a StateSnapshot after each timestep.
These snapshots are collected into a StateHistory, which can be
played back at any speed, exported, or analysed.

Design:
    - Snapshots are deep copies — mutating the simulation does not
      affect recorded history.
    - EntityState stores per-entity physics data (pos, vel, acc, energy).
    - SimulationState stores the entire world at one instant.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from physengine.math.vector import Vector2


# ===========================================================================
#  Per-Entity State
# ===========================================================================
@dataclass(frozen=True, slots=True)
class EntityState:
    """Frozen snapshot of one entity's physical state at a point in time.

    Attributes:
        entity_id: Unique identifier of the entity.
        name: Human-readable name.
        position: Position in world coordinates.
        velocity: Linear velocity.
        acceleration: Linear acceleration.
        rotation: Rotation angle (radians).
        angular_velocity: Angular velocity (rad/s).
        mass: Mass (kg).
        kinetic_energy: ½mv² at this instant.
        momentum: p = mv at this instant.
    """

    entity_id: str
    name: str
    position: Vector2
    velocity: Vector2
    acceleration: Vector2
    rotation: float = 0.0
    angular_velocity: float = 0.0
    mass: float = 1.0
    kinetic_energy: float = 0.0
    momentum: Vector2 = field(default_factory=Vector2.zero)

    @classmethod
    def from_entity(cls, entity: object) -> EntityState:
        """Create an EntityState from a live Entity.

        This import is deferred to avoid circular imports.
        The entity parameter should be a physengine.core.entity.Entity.
        """
        from physengine.core.entity import Entity, RigidBodyComponent, Transform

        assert isinstance(entity, Entity)

        transform = entity.get_component(Transform)
        pos = transform.position
        rot = transform.rotation

        if entity.has_component(RigidBodyComponent):
            rb = entity.get_component(RigidBodyComponent)
            vel = rb.velocity
            acc = rb.acceleration
            mass = rb.mass
            ang_vel = rb.angular_velocity
            ke = 0.5 * mass * vel.magnitude_squared
            mom = vel * mass
        else:
            vel = Vector2.zero()
            acc = Vector2.zero()
            mass = 0.0
            ang_vel = 0.0
            ke = 0.0
            mom = Vector2.zero()

        return cls(
            entity_id=entity.id,
            name=entity.name,
            position=Vector2(pos.x, pos.y),  # defensive copy
            velocity=Vector2(vel.x, vel.y),
            acceleration=Vector2(acc.x, acc.y),
            rotation=rot,
            angular_velocity=ang_vel,
            mass=mass,
            kinetic_energy=ke,
            momentum=mom,
        )


# ===========================================================================
#  Full Simulation State
# ===========================================================================
@dataclass(frozen=True, slots=True)
class SimulationState:
    """Frozen snapshot of the entire simulation at one instant.

    Attributes:
        time: Simulation time (seconds).
        step: Step number.
        entities: Mapping from entity_id to EntityState.
        total_kinetic_energy: Sum of all entities' kinetic energy.
        total_momentum: Sum of all entities' momentum vectors.
    """

    time: float
    step: int
    entities: dict[str, EntityState]
    total_kinetic_energy: float = 0.0
    total_momentum: Vector2 = field(default_factory=Vector2.zero)

    def get_entity(self, name_or_id: str) -> EntityState:
        """Look up an entity state by name or ID.

        Tries ID first, then searches by name.

        Raises:
            KeyError: If not found.
        """
        if name_or_id in self.entities:
            return self.entities[name_or_id]
        for es in self.entities.values():
            if es.name == name_or_id:
                return es
        raise KeyError(f"Entity '{name_or_id}' not found in state at t={self.time}")


# ===========================================================================
#  State History
# ===========================================================================
class StateHistory:
    """Ordered collection of SimulationState snapshots.

    Provides convenient access to the full timeline and
    per-entity trajectories for analysis and rendering.
    """

    def __init__(self, max_size: int | None = None) -> None:
        """
        Args:
            max_size: Optional maximum number of snapshots to retain.
                      Oldest snapshots are discarded when the limit is reached
                      (ring-buffer behavior).
        """
        self._snapshots: list[SimulationState] = []
        self._max_size = max_size

    def record(self, state: SimulationState) -> None:
        """Add a snapshot to the history."""
        self._snapshots.append(state)
        if self._max_size is not None and len(self._snapshots) > self._max_size:
            self._snapshots.pop(0)

    def clear(self) -> None:
        """Remove all recorded snapshots."""
        self._snapshots.clear()

    @property
    def snapshots(self) -> list[SimulationState]:
        """All recorded snapshots in chronological order."""
        return list(self._snapshots)

    @property
    def times(self) -> list[float]:
        """List of simulation times for all snapshots."""
        return [s.time for s in self._snapshots]

    def __len__(self) -> int:
        return len(self._snapshots)

    def __getitem__(self, index: int) -> SimulationState:
        return self._snapshots[index]

    @property
    def first(self) -> SimulationState | None:
        """First (earliest) snapshot, or None if empty."""
        return self._snapshots[0] if self._snapshots else None

    @property
    def last(self) -> SimulationState | None:
        """Last (latest) snapshot, or None if empty."""
        return self._snapshots[-1] if self._snapshots else None

    def get_entity_positions(self, name_or_id: str) -> list[Vector2]:
        """Extract the position trajectory for a named entity.

        Args:
            name_or_id: Entity name or ID.

        Returns:
            List of Vector2 positions in chronological order.
        """
        positions: list[Vector2] = []
        for snap in self._snapshots:
            try:
                es = snap.get_entity(name_or_id)
                positions.append(es.position)
            except KeyError:
                pass
        return positions

    def get_entity_velocities(self, name_or_id: str) -> list[Vector2]:
        """Extract the velocity trajectory for a named entity."""
        velocities: list[Vector2] = []
        for snap in self._snapshots:
            try:
                es = snap.get_entity(name_or_id)
                velocities.append(es.velocity)
            except KeyError:
                pass
        return velocities

    def get_entity_kinetic_energies(self, name_or_id: str) -> list[float]:
        """Extract kinetic energy over time for a named entity."""
        energies: list[float] = []
        for snap in self._snapshots:
            try:
                es = snap.get_entity(name_or_id)
                energies.append(es.kinetic_energy)
            except KeyError:
                pass
        return energies

    def total_kinetic_energies(self) -> list[float]:
        """Total kinetic energy of the system at each timestep."""
        return [s.total_kinetic_energy for s in self._snapshots]

    def total_momenta(self) -> list[Vector2]:
        """Total momentum vector of the system at each timestep."""
        return [s.total_momentum for s in self._snapshots]
