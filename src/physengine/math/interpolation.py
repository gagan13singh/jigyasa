"""
physengine.math.interpolation
=============================

Interpolation utilities for smooth trajectory replay and animation curves.

These are used by the analysis/recording layer to provide smooth playback
at arbitrary time resolution, even if the simulation was run at a fixed
timestep.
"""

from __future__ import annotations

import math
from typing import TypeVar

from physengine.math.vector import Vector2, Vector3

T = TypeVar("T", float, Vector2, Vector3)


# ===========================================================================
#  Scalar Interpolation
# ===========================================================================
def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between scalars *a* and *b*.

    Args:
        a: Start value (returned when t=0).
        b: End value (returned when t=1).
        t: Interpolation parameter.

    Returns:
        The interpolated value.
    """
    return a + (b - a) * t


def inverse_lerp(a: float, b: float, value: float) -> float:
    """Compute the interpolation parameter *t* such that lerp(a, b, t) = value.

    Args:
        a: Start value.
        b: End value.
        value: The value to find the parameter for.

    Returns:
        The parameter t ∈ [0, 1] if value is between a and b.

    Raises:
        ValueError: If a == b.
    """
    if abs(b - a) < 1e-15:
        raise ValueError("Cannot inverse_lerp when a == b")
    return (value - a) / (b - a)


def clamp(value: float, low: float, high: float) -> float:
    """Clamp *value* to the range [low, high]."""
    return max(low, min(high, value))


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """Hermite smoothstep interpolation.

    Returns 0 if x ≤ edge0, 1 if x ≥ edge1, and smoothly interpolates
    between 0 and 1 using a cubic polynomial for edge0 < x < edge1.
    """
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def smootherstep(edge0: float, edge1: float, x: float) -> float:
    """Ken Perlin's improved smoothstep (C² continuous).

    Uses a 5th-degree polynomial for even smoother transitions.
    """
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


# ===========================================================================
#  Easing Functions (for animation)
# ===========================================================================
def ease_in_quad(t: float) -> float:
    """Quadratic ease-in: starts slow, ends fast."""
    return t * t


def ease_out_quad(t: float) -> float:
    """Quadratic ease-out: starts fast, ends slow."""
    return t * (2.0 - t)


def ease_in_out_quad(t: float) -> float:
    """Quadratic ease-in-out: smooth start and end."""
    if t < 0.5:
        return 2.0 * t * t
    return -1.0 + (4.0 - 2.0 * t) * t


def ease_in_cubic(t: float) -> float:
    """Cubic ease-in."""
    return t * t * t


def ease_out_cubic(t: float) -> float:
    """Cubic ease-out."""
    t -= 1.0
    return t * t * t + 1.0


def ease_in_out_sine(t: float) -> float:
    """Sinusoidal ease-in-out."""
    return 0.5 * (1.0 - math.cos(math.pi * t))


# ===========================================================================
#  Spline Interpolation
# ===========================================================================
def cubic_hermite(
    p0: float, m0: float, p1: float, m1: float, t: float
) -> float:
    """Cubic Hermite interpolation between two points with tangents.

    Args:
        p0: Value at start.
        m0: Tangent at start.
        p1: Value at end.
        m1: Tangent at end.
        t: Parameter in [0, 1].

    Returns:
        Interpolated value.
    """
    t2 = t * t
    t3 = t2 * t
    h00 = 2 * t3 - 3 * t2 + 1
    h10 = t3 - 2 * t2 + t
    h01 = -2 * t3 + 3 * t2
    h11 = t3 - t2
    return h00 * p0 + h10 * m0 + h01 * p1 + h11 * m1


def catmull_rom(
    p0: float, p1: float, p2: float, p3: float, t: float
) -> float:
    """Catmull–Rom spline interpolation through four control points.

    Interpolates between p1 and p2, using p0 and p3 to define tangents.

    Args:
        p0: Control point before the segment.
        p1: Start of the interpolated segment.
        p2: End of the interpolated segment.
        p3: Control point after the segment.
        t: Parameter in [0, 1].

    Returns:
        Interpolated value at parameter *t* between p1 and p2.
    """
    m0 = 0.5 * (p2 - p0)
    m1 = 0.5 * (p3 - p1)
    return cubic_hermite(p1, m0, p2, m1, t)


def catmull_rom_vector2(
    p0: Vector2, p1: Vector2, p2: Vector2, p3: Vector2, t: float
) -> Vector2:
    """Catmull–Rom interpolation for Vector2 control points."""
    return Vector2(
        catmull_rom(p0.x, p1.x, p2.x, p3.x, t),
        catmull_rom(p0.y, p1.y, p2.y, p3.y, t),
    )


def catmull_rom_vector3(
    p0: Vector3, p1: Vector3, p2: Vector3, p3: Vector3, t: float
) -> Vector3:
    """Catmull–Rom interpolation for Vector3 control points."""
    return Vector3(
        catmull_rom(p0.x, p1.x, p2.x, p3.x, t),
        catmull_rom(p0.y, p1.y, p2.y, p3.y, t),
        catmull_rom(p0.z, p1.z, p2.z, p3.z, t),
    )


# ===========================================================================
#  Trajectory Resampling (used by recorder & rendering)
# ===========================================================================
def resample_trajectory(
    times: list[float],
    values: list[float],
    target_times: list[float],
) -> list[float]:
    """Resample a time-series using linear interpolation.

    Args:
        times: Monotonically increasing time stamps.
        values: Corresponding values.
        target_times: Desired output time stamps.

    Returns:
        List of interpolated values at *target_times*.
    """
    if len(times) != len(values):
        raise ValueError("times and values must have the same length")
    if not times:
        return []

    result: list[float] = []
    j = 0
    n = len(times)

    for tt in target_times:
        # Advance to the segment containing tt
        while j < n - 2 and times[j + 1] < tt:
            j += 1

        if tt <= times[0]:
            result.append(values[0])
        elif tt >= times[-1]:
            result.append(values[-1])
        else:
            dt = times[j + 1] - times[j]
            if dt < 1e-15:
                result.append(values[j])
            else:
                t_local = (tt - times[j]) / dt
                result.append(lerp(values[j], values[j + 1], t_local))

    return result
