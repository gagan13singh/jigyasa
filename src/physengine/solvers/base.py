"""
physengine.solvers.base
=======================

Abstract integrator interface.

All numerical integrators implement the Integrator protocol.
This allows the simulation to swap solvers without changing any physics code.

    sim = Simulation(world, integrator=RK4Integrator())

The key method is ``step()``, which takes the current state and returns
the new state after advancing by dt.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from physengine.math.vector import Vector2

# Type alias for the acceleration function used by multi-step integrators.
# Given (position, velocity) → acceleration
AccelerationFn = Callable[[Vector2, Vector2], Vector2]


class Integrator(ABC):
    """Abstract base class for numerical integrators.

    An integrator advances the position and velocity of a body by one
    timestep, given the current acceleration (or an acceleration function).
    """

    @abstractmethod
    def step(
        self,
        position: Vector2,
        velocity: Vector2,
        acceleration: Vector2,
        dt: float,
        acceleration_fn: AccelerationFn | None = None,
    ) -> tuple[Vector2, Vector2]:
        """Advance one timestep.

        Args:
            position: Current position.
            velocity: Current velocity.
            acceleration: Current acceleration (from accumulated forces).
            dt: Timestep size (seconds).
            acceleration_fn: Optional callable (pos, vel) → acc for
                             multi-evaluation integrators (RK4).
                             If None, acceleration is treated as constant
                             throughout the timestep.

        Returns:
            (new_position, new_velocity) after the timestep.
        """
        ...

    @property
    def name(self) -> str:
        """Human-readable name."""
        return type(self).__name__

    @property
    def order(self) -> int:
        """Order of accuracy of the integrator.

        - Euler: 1st order
        - Verlet: 2nd order
        - RK4: 4th order
        """
        return 1

    def __repr__(self) -> str:
        return f"{self.name}(order={self.order})"
