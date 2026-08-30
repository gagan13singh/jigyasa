"""
physengine.core.config
======================

Simulation configuration management.

Provides a central configuration object for simulation parameters,
with sensible defaults and support for loading from dicts / files.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from physengine.math.constants import DEFAULT_TIMESTEP, STANDARD_GRAVITY
from physengine.math.vector import Vector2


@dataclass
class SimulationConfig:
    """Configuration for a simulation run.

    Attributes:
        timestep: Fixed timestep per integration step (seconds).
        duration: Total simulation duration (seconds). 0 = run indefinitely.
        gravity: Gravity vector (m/s²). Defaults to Earth surface gravity.
        integrator_name: Name of the integrator to use.
                         Options: "euler", "semi_implicit_euler", "verlet", "rk4".
        substeps: Number of sub-steps per timestep for accuracy.
        record_interval: Record state every N steps (1 = every step).
        max_history_size: Maximum number of state snapshots to keep.
                          None = unlimited.
        air_density: Air density for drag calculations (kg/m³).
        enable_recording: Whether to record simulation history.
        name: Human-readable name for this simulation.
    """

    timestep: float = DEFAULT_TIMESTEP
    duration: float = 10.0
    gravity: Vector2 = field(default_factory=lambda: Vector2(0.0, -STANDARD_GRAVITY))
    integrator_name: str = "rk4"
    substeps: int = 1
    record_interval: int = 1
    max_history_size: int | None = None
    air_density: float = 1.225
    enable_recording: bool = True
    name: str = "Untitled Simulation"

    def __post_init__(self) -> None:
        if self.timestep <= 0:
            raise ValueError(f"Timestep must be positive, got {self.timestep}")
        if self.duration < 0:
            raise ValueError(f"Duration must be non-negative, got {self.duration}")
        if self.substeps < 1:
            raise ValueError(f"Substeps must be ≥ 1, got {self.substeps}")

    @property
    def effective_dt(self) -> float:
        """Actual integration timestep accounting for substeps."""
        return self.timestep / self.substeps

    @classmethod
    def from_dict(cls, data: dict) -> SimulationConfig:
        """Create config from a dictionary.

        Supports nested gravity as [x, y] or {"x": ..., "y": ...}.
        """
        config = cls()

        if "timestep" in data:
            config.timestep = float(data["timestep"])
        if "duration" in data:
            config.duration = float(data["duration"])
        if "gravity" in data:
            g = data["gravity"]
            if isinstance(g, (list, tuple)):
                config.gravity = Vector2(float(g[0]), float(g[1]))
            elif isinstance(g, dict):
                config.gravity = Vector2(float(g.get("x", 0)), float(g.get("y", -9.81)))
            elif isinstance(g, (int, float)):
                config.gravity = Vector2(0.0, -float(g))
        if "integrator" in data:
            config.integrator_name = str(data["integrator"])
        if "substeps" in data:
            config.substeps = int(data["substeps"])
        if "record_interval" in data:
            config.record_interval = int(data["record_interval"])
        if "max_history_size" in data:
            val = data["max_history_size"]
            config.max_history_size = int(val) if val else None
        if "air_density" in data:
            config.air_density = float(data["air_density"])
        if "enable_recording" in data:
            config.enable_recording = bool(data["enable_recording"])
        if "name" in data:
            config.name = str(data["name"])

        return config

    def to_dict(self) -> dict:
        """Serialize config to a dictionary."""
        return {
            "timestep": self.timestep,
            "duration": self.duration,
            "gravity": [self.gravity.x, self.gravity.y],
            "integrator": self.integrator_name,
            "substeps": self.substeps,
            "record_interval": self.record_interval,
            "max_history_size": self.max_history_size,
            "air_density": self.air_density,
            "enable_recording": self.enable_recording,
            "name": self.name,
        }
