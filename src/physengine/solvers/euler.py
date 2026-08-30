"""
physengine.solvers.euler
========================

Euler family integrators.

EulerIntegrator (Forward Euler):
    x_{n+1} = x_n + v_n * dt
    v_{n+1} = v_n + a_n * dt

    Simple but inaccurate.  Energy grows without bound in oscillatory
    systems.  1st order.  Useful as a baseline for comparison.

SemiImplicitEulerIntegrator (Symplectic Euler):
    v_{n+1} = v_n + a_n * dt
    x_{n+1} = x_n + v_{n+1} * dt    ← uses UPDATED velocity

    Same cost as forward Euler but much better energy conservation.
    Symplectic: preserves phase-space volume, so energy stays bounded.
    Widely used in games.
"""

from __future__ import annotations

from physengine.math.vector import Vector2
from physengine.solvers.base import AccelerationFn, Integrator


class EulerIntegrator(Integrator):
    """Forward (explicit) Euler integration — 1st order.

    Simple but introduces systematic energy drift.
    Use for comparison and education, not production simulations.
    """

    def step(
        self,
        position: Vector2,
        velocity: Vector2,
        acceleration: Vector2,
        dt: float,
        acceleration_fn: AccelerationFn | None = None,
    ) -> tuple[Vector2, Vector2]:
        # x_{n+1} = x_n + v_n * dt
        new_position = position + velocity * dt
        # v_{n+1} = v_n + a_n * dt
        new_velocity = velocity + acceleration * dt
        return new_position, new_velocity

    @property
    def order(self) -> int:
        return 1


class SemiImplicitEulerIntegrator(Integrator):
    """Semi-implicit (symplectic) Euler integration — 1st order, energy-stable.

    Updates velocity first, then uses the new velocity to update position.
    This makes it symplectic — energy oscillates around the true value
    rather than drifting monotonically.
    """

    def step(
        self,
        position: Vector2,
        velocity: Vector2,
        acceleration: Vector2,
        dt: float,
        acceleration_fn: AccelerationFn | None = None,
    ) -> tuple[Vector2, Vector2]:
        # v_{n+1} = v_n + a_n * dt  (velocity updated FIRST)
        new_velocity = velocity + acceleration * dt
        # x_{n+1} = x_n + v_{n+1} * dt  (uses NEW velocity)
        new_position = position + new_velocity * dt
        return new_position, new_velocity

    @property
    def name(self) -> str:
        return "SemiImplicitEuler"

    @property
    def order(self) -> int:
        return 1
