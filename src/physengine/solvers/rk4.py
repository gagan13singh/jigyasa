"""
physengine.solvers.rk4
======================

Classic 4th-order Runge-Kutta integrator.

Algorithm:
    k1_v = a(x_n,        v_n)             * dt
    k1_x = v_n                             * dt

    k2_v = a(x_n + k1_x/2, v_n + k1_v/2)  * dt
    k2_x = (v_n + k1_v/2)                  * dt

    k3_v = a(x_n + k2_x/2, v_n + k2_v/2)  * dt
    k3_x = (v_n + k2_v/2)                  * dt

    k4_v = a(x_n + k3_x, v_n + k3_v)      * dt
    k4_x = (v_n + k3_v)                    * dt

    x_{n+1} = x_n + (k1_x + 2*k2_x + 2*k3_x + k4_x) / 6
    v_{n+1} = v_n + (k1_v + 2*k2_v + 2*k3_v + k4_v) / 6

Advantages:
    - 4th order accuracy (error ∝ dt⁴)
    - Extremely accurate for smooth force fields
    - Well-suited for educational comparison with lower-order methods

Disadvantages:
    - 4 force evaluations per step (4× more expensive than Euler)
    - Not symplectic — energy can drift over very long simulations
    - Overkill for simple constant-acceleration problems

Requires acceleration_fn for full accuracy.  Falls back to constant
acceleration if not provided (effectively becomes 4th-order with
constant derivatives, which degenerates to exact for linear systems).
"""

from __future__ import annotations

from physengine.math.vector import Vector2
from physengine.solvers.base import AccelerationFn, Integrator


class RK4Integrator(Integrator):
    """Classic 4th-order Runge-Kutta integrator.

    Highest accuracy per step of all built-in integrators.
    Best choice when accuracy matters more than performance.
    """

    def step(
        self,
        position: Vector2,
        velocity: Vector2,
        acceleration: Vector2,
        dt: float,
        acceleration_fn: AccelerationFn | None = None,
    ) -> tuple[Vector2, Vector2]:
        if acceleration_fn is None:
            # Without acceleration_fn, treat as constant acceleration
            # This is exact for constant-acceleration problems
            new_velocity = velocity + acceleration * dt
            new_position = position + velocity * dt + acceleration * (0.5 * dt * dt)
            return new_position, new_velocity

        # ── Stage 1: Evaluate at current state ──────────────────────
        a1 = acceleration_fn(position, velocity)
        k1_v = a1 * dt
        k1_x = velocity * dt

        # ── Stage 2: Evaluate at midpoint using stage 1 ────────────
        mid_pos_2 = position + k1_x * 0.5
        mid_vel_2 = velocity + k1_v * 0.5
        a2 = acceleration_fn(mid_pos_2, mid_vel_2)
        k2_v = a2 * dt
        k2_x = mid_vel_2 * dt

        # ── Stage 3: Evaluate at midpoint using stage 2 ────────────
        mid_pos_3 = position + k2_x * 0.5
        mid_vel_3 = velocity + k2_v * 0.5
        a3 = acceleration_fn(mid_pos_3, mid_vel_3)
        k3_v = a3 * dt
        k3_x = mid_vel_3 * dt

        # ── Stage 4: Evaluate at endpoint using stage 3 ────────────
        end_pos = position + k3_x
        end_vel = velocity + k3_v
        a4 = acceleration_fn(end_pos, end_vel)
        k4_v = a4 * dt
        k4_x = end_vel * dt

        # ── Combine: weighted average ──────────────────────────────
        new_position = position + (k1_x + k2_x * 2 + k3_x * 2 + k4_x) * (1.0 / 6.0)
        new_velocity = velocity + (k1_v + k2_v * 2 + k3_v * 2 + k4_v) * (1.0 / 6.0)

        return new_position, new_velocity

    @property
    def name(self) -> str:
        return "RK4"

    @property
    def order(self) -> int:
        return 4
