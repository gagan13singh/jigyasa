"""
physengine.analysis.trajectory
==============================

Structured trajectory data for a single entity.

A Trajectory holds the complete time-series of an entity's motion:
position, velocity, acceleration, and energy at each recorded timestep.

It provides convenient access methods and export capabilities.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from physengine.math.vector import Vector2


class Trajectory:
    """Time-series data for one entity's motion.

    Attributes:
        entity_name: Name of the entity this trajectory belongs to.
        times: List of simulation timestamps.
        positions: List of position vectors.
        velocities: List of velocity vectors.
        accelerations: List of acceleration vectors.
        kinetic_energies: List of kinetic energies.
    """

    def __init__(
        self,
        entity_name: str,
        times: list[float],
        positions: list[Vector2],
        velocities: list[Vector2],
        accelerations: list[Vector2],
        kinetic_energies: list[float] | None = None,
    ) -> None:
        self.entity_name = entity_name
        self.times = times
        self.positions = positions
        self.velocities = velocities
        self.accelerations = accelerations
        self.kinetic_energies = kinetic_energies or [0.0] * len(times)

    @property
    def num_points(self) -> int:
        """Number of data points in the trajectory."""
        return len(self.times)

    @property
    def duration(self) -> float:
        """Duration of the trajectory."""
        if not self.times:
            return 0.0
        return self.times[-1] - self.times[0]

    # -- Convenience accessors -----------------------------------------------
    def x_positions(self) -> list[float]:
        """X coordinates over time."""
        return [p.x for p in self.positions]

    def y_positions(self) -> list[float]:
        """Y coordinates over time."""
        return [p.y for p in self.positions]

    def x_velocities(self) -> list[float]:
        """X velocity components over time."""
        return [v.x for v in self.velocities]

    def y_velocities(self) -> list[float]:
        """Y velocity components over time."""
        return [v.y for v in self.velocities]

    def speeds(self) -> list[float]:
        """Scalar speed over time."""
        return [v.magnitude for v in self.velocities]

    def x_accelerations(self) -> list[float]:
        """X acceleration components over time."""
        return [a.x for a in self.accelerations]

    def y_accelerations(self) -> list[float]:
        """Y acceleration components over time."""
        return [a.y for a in self.accelerations]

    # -- NumPy conversion ----------------------------------------------------
    def positions_array(self) -> NDArray[np.float64]:
        """Positions as an Nx2 numpy array."""
        return np.array([[p.x, p.y] for p in self.positions], dtype=np.float64)

    def velocities_array(self) -> NDArray[np.float64]:
        """Velocities as an Nx2 numpy array."""
        return np.array([[v.x, v.y] for v in self.velocities], dtype=np.float64)

    def times_array(self) -> NDArray[np.float64]:
        """Times as a 1D numpy array."""
        return np.array(self.times, dtype=np.float64)

    # -- Export --------------------------------------------------------------
    def to_csv(self, path: str | Path) -> None:
        """Export trajectory to CSV file.

        Columns: time, x, y, vx, vy, ax, ay, speed, KE
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["time", "x", "y", "vx", "vy", "ax", "ay", "speed", "KE"])
            for i in range(self.num_points):
                writer.writerow([
                    f"{self.times[i]:.6f}",
                    f"{self.positions[i].x:.6f}",
                    f"{self.positions[i].y:.6f}",
                    f"{self.velocities[i].x:.6f}",
                    f"{self.velocities[i].y:.6f}",
                    f"{self.accelerations[i].x:.6f}",
                    f"{self.accelerations[i].y:.6f}",
                    f"{self.velocities[i].magnitude:.6f}",
                    f"{self.kinetic_energies[i]:.6f}",
                ])

    def to_json(self, path: str | Path) -> None:
        """Export trajectory to JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "entity_name": self.entity_name,
            "num_points": self.num_points,
            "duration": self.duration,
            "data": [
                {
                    "t": self.times[i],
                    "x": self.positions[i].x,
                    "y": self.positions[i].y,
                    "vx": self.velocities[i].x,
                    "vy": self.velocities[i].y,
                    "ax": self.accelerations[i].x,
                    "ay": self.accelerations[i].y,
                    "speed": self.velocities[i].magnitude,
                    "KE": self.kinetic_energies[i],
                }
                for i in range(self.num_points)
            ],
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def to_dict_list(self) -> list[dict]:
        """Convert to a list of dictionaries (one per timestep)."""
        return [
            {
                "t": self.times[i],
                "x": self.positions[i].x,
                "y": self.positions[i].y,
                "vx": self.velocities[i].x,
                "vy": self.velocities[i].y,
                "ax": self.accelerations[i].x,
                "ay": self.accelerations[i].y,
            }
            for i in range(self.num_points)
        ]

    def __repr__(self) -> str:
        return (
            f"Trajectory(entity={self.entity_name!r}, "
            f"points={self.num_points}, "
            f"duration={self.duration:.4f}s)"
        )

    def __len__(self) -> int:
        return self.num_points
