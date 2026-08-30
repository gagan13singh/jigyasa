"""
physengine.analysis.recorder
============================

High-level recording interface that wraps StateHistory with
convenient entity-level access.

The StateRecorder sits between the simulation and analysis layer,
providing trajectory extraction, time-series data, and export-ready formats.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from physengine.analysis.trajectory import Trajectory
from physengine.core.state import StateHistory
from physengine.math.vector import Vector2

if TYPE_CHECKING:
    from physengine.core.simulation import Simulation


class StateRecorder:
    """Extracts and organizes recorded simulation data.

    This class wraps a StateHistory (from a completed simulation)
    and provides high-level access to per-entity trajectories
    and system-level measurements.

    Usage:
        >>> sim = Simulation(world)
        >>> sim.run(10.0)
        >>> recorder = StateRecorder(sim.history)
        >>> traj = recorder.get_trajectory("ball")
        >>> traj.positions()  # list of Vector2
    """

    def __init__(self, history: StateHistory) -> None:
        self._history = history
        self._trajectory_cache: dict[str, Trajectory] = {}

    @classmethod
    def from_simulation(cls, simulation: Simulation) -> StateRecorder:
        """Create a recorder from a completed simulation."""
        return cls(simulation.history)

    def get_trajectory(self, entity_name_or_id: str) -> Trajectory:
        """Extract the full trajectory for a named entity.

        Args:
            entity_name_or_id: Entity name or ID.

        Returns:
            Trajectory object with position, velocity, acceleration over time.
        """
        if entity_name_or_id in self._trajectory_cache:
            return self._trajectory_cache[entity_name_or_id]

        times: list[float] = []
        positions: list[Vector2] = []
        velocities: list[Vector2] = []
        accelerations: list[Vector2] = []
        kinetic_energies: list[float] = []

        for snapshot in self._history.snapshots:
            try:
                es = snapshot.get_entity(entity_name_or_id)
            except KeyError:
                continue

            times.append(snapshot.time)
            positions.append(es.position)
            velocities.append(es.velocity)
            accelerations.append(es.acceleration)
            kinetic_energies.append(es.kinetic_energy)

        traj = Trajectory(
            entity_name=entity_name_or_id,
            times=times,
            positions=positions,
            velocities=velocities,
            accelerations=accelerations,
            kinetic_energies=kinetic_energies,
        )

        self._trajectory_cache[entity_name_or_id] = traj
        return traj

    @property
    def entity_names(self) -> list[str]:
        """Names of all entities that appear in the history."""
        if not self._history.snapshots:
            return []
        names: set[str] = set()
        for snapshot in self._history.snapshots:
            for es in snapshot.entities.values():
                names.add(es.name)
        return sorted(names)

    @property
    def times(self) -> list[float]:
        """Simulation timestamps."""
        return self._history.times

    @property
    def duration(self) -> float:
        """Total simulation duration."""
        if not self._history.snapshots:
            return 0.0
        return self._history.snapshots[-1].time - self._history.snapshots[0].time

    @property
    def total_kinetic_energies(self) -> list[float]:
        """Total system KE at each recorded timestep."""
        return self._history.total_kinetic_energies()

    @property
    def total_momenta(self) -> list[Vector2]:
        """Total system momentum at each recorded timestep."""
        return self._history.total_momenta()
