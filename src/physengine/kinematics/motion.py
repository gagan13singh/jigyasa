"""
physengine.kinematics.motion
============================

Analytical solutions for uniform and uniformly accelerated motion.

These are EXACT solutions — no numerical error.  Used to:
1. Validate numerical integrators against known answers
2. Provide instant calculations for simple problems (Vidyastra)
3. Compute reference trajectories for error analysis
"""

from __future__ import annotations

import math

from physengine.math.vector import Vector2


def position_1d(x0: float, v0: float, a: float, t: float) -> float:
    """Position in 1D uniformly accelerated motion.

    x(t) = x₀ + v₀t + ½at²
    """
    return x0 + v0 * t + 0.5 * a * t * t


def velocity_1d(v0: float, a: float, t: float) -> float:
    """Velocity in 1D uniformly accelerated motion.

    v(t) = v₀ + at
    """
    return v0 + a * t


def position_2d(
    pos0: Vector2,
    vel0: Vector2,
    acc: Vector2,
    t: float,
) -> Vector2:
    """Position in 2D uniformly accelerated motion.

    r(t) = r₀ + v₀t + ½at²
    """
    return pos0 + vel0 * t + acc * (0.5 * t * t)


def velocity_2d(
    vel0: Vector2,
    acc: Vector2,
    t: float,
) -> Vector2:
    """Velocity in 2D uniformly accelerated motion.

    v(t) = v₀ + at
    """
    return vel0 + acc * t


def time_to_reach_velocity(v0: float, a: float, v_target: float) -> float:
    """Time to reach a target velocity.

    t = (v_target - v₀) / a

    Raises:
        ValueError: If acceleration is zero.
    """
    if abs(a) < 1e-15:
        raise ValueError("Cannot reach target velocity with zero acceleration")
    return (v_target - v0) / a


def displacement_given_velocities(v0: float, v_final: float, a: float) -> float:
    """Displacement between two velocities.

    v² = v₀² + 2a·Δx  →  Δx = (v² - v₀²) / (2a)

    Raises:
        ValueError: If acceleration is zero.
    """
    if abs(a) < 1e-15:
        raise ValueError("Cannot compute displacement with zero acceleration")
    return (v_final * v_final - v0 * v0) / (2.0 * a)


def velocity_from_displacement(v0: float, a: float, displacement: float) -> float:
    """Final velocity after a given displacement.

    v² = v₀² + 2a·Δx  →  v = √(v₀² + 2a·Δx)

    Raises:
        ValueError: If the result would be imaginary.
    """
    discriminant = v0 * v0 + 2.0 * a * displacement
    if discriminant < 0:
        raise ValueError(
            f"Cannot compute velocity: v₀²+2aΔx = {discriminant:.6g} < 0 "
            f"(object stops before reaching displacement)"
        )
    return math.sqrt(discriminant)
