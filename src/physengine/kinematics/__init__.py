"""
physengine.kinematics
=====================

Analytical kinematic solutions (exact, no numerical error).
"""

from physengine.kinematics.motion import (
    displacement_given_velocities,
    position_1d,
    position_2d,
    time_to_reach_velocity,
    velocity_1d,
    velocity_2d,
    velocity_from_displacement,
)
from physengine.kinematics.projectile import (
    ProjectileMotion,
    max_range,
    optimal_angle_for_range,
    range_at_angle,
)

__all__ = [
    "ProjectileMotion",
    "displacement_given_velocities",
    "max_range",
    "optimal_angle_for_range",
    "position_1d",
    "position_2d",
    "range_at_angle",
    "time_to_reach_velocity",
    "velocity_1d",
    "velocity_2d",
    "velocity_from_displacement",
]
