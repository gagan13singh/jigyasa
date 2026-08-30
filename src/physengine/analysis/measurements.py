"""
physengine.analysis.measurements
================================

Scientific measurement and validation tools.

Used to:
1. Measure energy drift (how well an integrator conserves energy)
2. Measure momentum conservation
3. Compare numerical results against analytical solutions
4. Compute error metrics (MAE, RMSE, max error)
"""

from __future__ import annotations

import math
from collections.abc import Callable

from physengine.analysis.trajectory import Trajectory
from physengine.math.vector import Vector2


# ===========================================================================
#  Energy Conservation Metrics
# ===========================================================================
def energy_drift(
    kinetic_energies: list[float],
    potential_energies: list[float] | None = None,
) -> dict[str, float]:
    """Measure energy drift over a simulation.

    Args:
        kinetic_energies: KE at each timestep.
        potential_energies: PE at each timestep (if available).

    Returns:
        Dictionary with:
            - initial_energy: Energy at t=0
            - final_energy: Energy at t_end
            - absolute_drift: |E_final - E_initial|
            - relative_drift: |E_final - E_initial| / |E_initial|
            - max_deviation: Maximum deviation from initial energy
    """
    if potential_energies is not None:
        total = [ke + pe for ke, pe in zip(kinetic_energies, potential_energies, strict=False)]
    else:
        total = kinetic_energies

    if not total:
        return {
            "initial_energy": 0.0,
            "final_energy": 0.0,
            "absolute_drift": 0.0,
            "relative_drift": 0.0,
            "max_deviation": 0.0,
        }

    e0 = total[0]
    e_final = total[-1]
    abs_drift = abs(e_final - e0)
    rel_drift = abs_drift / abs(e0) if abs(e0) > 1e-15 else 0.0
    max_dev = max(abs(e - e0) for e in total)

    return {
        "initial_energy": e0,
        "final_energy": e_final,
        "absolute_drift": abs_drift,
        "relative_drift": rel_drift,
        "max_deviation": max_dev,
    }


# ===========================================================================
#  Momentum Conservation
# ===========================================================================
def momentum_conservation(momenta: list[Vector2]) -> dict[str, float]:
    """Measure how well momentum is conserved.

    Args:
        momenta: Total system momentum at each timestep.

    Returns:
        Dictionary with:
            - initial_momentum_magnitude: |p| at t=0
            - max_deviation: Maximum |p(t) - p(0)|
            - relative_deviation: max_deviation / |p(0)|
    """
    if not momenta:
        return {
            "initial_momentum_magnitude": 0.0,
            "max_deviation": 0.0,
            "relative_deviation": 0.0,
        }

    p0 = momenta[0]
    p0_mag = p0.magnitude
    max_dev = max(p.distance_to(p0) for p in momenta)
    rel_dev = max_dev / p0_mag if p0_mag > 1e-15 else 0.0

    return {
        "initial_momentum_magnitude": p0_mag,
        "max_deviation": max_dev,
        "relative_deviation": rel_dev,
    }


# ===========================================================================
#  Comparison with Analytical Solutions
# ===========================================================================
def compare_trajectory_with_analytical(
    trajectory: Trajectory,
    analytical_position: Callable[[float], Vector2],
) -> dict[str, float]:
    """Compare a numerical trajectory against an analytical solution.

    Args:
        trajectory: Numerical trajectory from simulation.
        analytical_position: Function t → position (exact solution).

    Returns:
        Dictionary with error metrics:
            - mae: Mean Absolute Error
            - rmse: Root Mean Square Error
            - max_error: Maximum position error
            - max_error_time: Time at which max error occurred
            - final_error: Error at the last timestep
    """
    errors: list[float] = []
    max_error = 0.0
    max_error_time = 0.0

    for t, num_pos in zip(trajectory.times, trajectory.positions, strict=False):
        exact_pos = analytical_position(t)
        error = num_pos.distance_to(exact_pos)
        errors.append(error)

        if error > max_error:
            max_error = error
            max_error_time = t

    n = len(errors)
    mae = sum(errors) / n if n > 0 else 0.0
    rmse = math.sqrt(sum(e * e for e in errors) / n) if n > 0 else 0.0

    return {
        "mae": mae,
        "rmse": rmse,
        "max_error": max_error,
        "max_error_time": max_error_time,
        "final_error": errors[-1] if errors else 0.0,
        "num_points": n,
    }


def compare_scalar_with_analytical(
    times: list[float],
    numerical: list[float],
    analytical: Callable[[float], float],
) -> dict[str, float]:
    """Compare a numerical scalar time-series against an analytical solution.

    Args:
        times: Timestamps.
        numerical: Numerical values.
        analytical: Function t → exact value.

    Returns:
        Error metrics: mae, rmse, max_error, max_error_time.
    """
    errors: list[float] = []
    max_error = 0.0
    max_error_time = 0.0

    for t, num_val in zip(times, numerical, strict=False):
        exact_val = analytical(t)
        error = abs(num_val - exact_val)
        errors.append(error)

        if error > max_error:
            max_error = error
            max_error_time = t

    n = len(errors)
    mae = sum(errors) / n if n > 0 else 0.0
    rmse = math.sqrt(sum(e * e for e in errors) / n) if n > 0 else 0.0

    return {
        "mae": mae,
        "rmse": rmse,
        "max_error": max_error,
        "max_error_time": max_error_time,
    }
