"""
physengine.solvers.verlet
=========================

Velocity Verlet integrator — 2nd order, symplectic.

Algorithm:
    x_{n+1} = x_n + v_n * dt + ½ * a_n * dt²
    a_{n+1} = f(x_{n+1}, v_n + a_n * dt)      ← re-evaluate acceleration
    v_{n+1} = v_n + ½ * (a_n + a_{n+1}) * dt

Advantages:
    - 2nd order accuracy (error ∝ dt²)
    - Symplectic: excellent long-term energy conservation
    - Only slightly more expensive than Euler
    - Standard choice for molecular dynamics and physics engines

Requires an acceleration_fn to re-evaluate forces at the new position.
If acceleration_fn is not provided, falls back to a simpler approximation.
"""

from __future__ import annotations

from physengine.math.vector import Vector2
from physengine.solvers.base import AccelerationFn, Integrator


class VelocityVerletIntegrator(Integrator):
    """Velocity Verlet integrator — 2nd order, symplectic.

    The gold standard for physics simulations that need good energy
    conservation without the cost of RK4.
    """

    def step(
        self,
        position: Vector2,
        velocity: Vector2,
        acceleration: Vector2,
        dt: float,
        acceleration_fn: AccelerationFn | None = None,
    ) -> tuple[Vector2, Vector2]:
        # Step 1: Update position using current velocity and acceleration
        # x_{n+1} = x_n + v_n * dt + ½ * a_n * dt²
        new_position = position + velocity * dt + acceleration * (0.5 * dt * dt)

        if acceleration_fn is not None:
            # Step 2: Compute new acceleration at the new position
            # Use an estimated velocity for the acceleration evaluation
            estimated_velocity = velocity + acceleration * dt
            new_acceleration = acceleration_fn(new_position, estimated_velocity)
        else:
            # Without acceleration_fn, assume constant acceleration
            new_acceleration = acceleration

        # Step 3: Update velocity using average of old and new acceleration
        # v_{n+1} = v_n + ½ * (a_n + a_{n+1}) * dt
        new_velocity = velocity + (acceleration + new_acceleration) * (0.5 * dt)

        return new_position, new_velocity

    @property
    def name(self) -> str:
        return "VelocityVerlet"

    @property
    def order(self) -> int:
        return 2
