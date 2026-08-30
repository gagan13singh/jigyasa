"""
physengine.mechanics.rotational
===============================

Rotational dynamics for Class 11 & Advanced Physics.

Features:
- Moment of Inertia (I) for standard geometries (Sphere, Cylinder, Ring, Rod)
- Parallel and Perpendicular axis theorems
- Torque: τ = r × F = I * α
- Angular momentum: L = I * ω
- Rotational kinetic energy: KE_rot = ½Iω²
- Rolling without slipping down an inclined plane:
    a = (g * sin θ) / (1 + I / (m * R²))
- Race of shapes down an incline (Sphere vs Cylinder vs Hoop)
"""

from __future__ import annotations

import enum
import math
from dataclasses import dataclass

from physengine.core.entity import Component
from physengine.math.constants import STANDARD_GRAVITY
from physengine.math.vector import Vector2


class InertiaShape(enum.Enum):
    """Standard geometrical shapes for moment of inertia calculation."""

    SOLID_SPHERE = "solid_sphere"      # I = 2/5 * m * R²  (k²/R² = 0.4)
    HOLLOW_SPHERE = "hollow_sphere"    # I = 2/3 * m * R²  (k²/R² = 0.667)
    SOLID_CYLINDER = "solid_cylinder"  # I = 1/2 * m * R²  (k²/R² = 0.5) (Disk)
    HOOP_OR_RING = "hoop_or_ring"      # I = 1 * m * R²    (k²/R² = 1.0)
    THIN_ROD_CENTER = "rod_center"     # I = 1/12 * m * L²
    THIN_ROD_END = "rod_end"           # I = 1/3 * m * L²
    POINT_MASS = "point_mass"          # I = m * R²


def moment_of_inertia(
    shape: InertiaShape,
    mass: float,
    radius: float = 1.0,
    length: float = 1.0,
) -> float:
    """Calculate the moment of inertia about the standard symmetry axis.

    Args:
        shape: Geometrical shape enum.
        mass: Mass (kg).
        radius: Radius (meters) for spheres, cylinders, rings.
        length: Length (meters) for rods.

    Returns:
        Moment of inertia (kg⋅m²).
    """
    if shape == InertiaShape.SOLID_SPHERE:
        return 0.4 * mass * radius * radius
    elif shape == InertiaShape.HOLLOW_SPHERE:
        return (2.0 / 3.0) * mass * radius * radius
    elif shape == InertiaShape.SOLID_CYLINDER:
        return 0.5 * mass * radius * radius
    elif shape == InertiaShape.HOOP_OR_RING:
        return 1.0 * mass * radius * radius
    elif shape == InertiaShape.THIN_ROD_CENTER:
        return (1.0 / 12.0) * mass * length * length
    elif shape == InertiaShape.THIN_ROD_END:
        return (1.0 / 3.0) * mass * length * length
    elif shape == InertiaShape.POINT_MASS:
        return mass * radius * radius
    return mass * radius * radius


def parallel_axis_theorem(I_cm: float, mass: float, distance: float) -> float:
    """I = I_cm + m * d²."""
    return I_cm + mass * distance * distance


def perpendicular_axis_theorem(I_x: float, I_y: float) -> float:
    """I_z = I_x + I_y (valid for planar laminar bodies)."""
    return I_x + I_y


@dataclass
class RotationalComponent(Component):
    """Component for entities undergoing rotational dynamics."""

    moment_of_inertia: float = 1.0
    angular_position: float = 0.0     # theta (radians)
    angular_velocity: float = 0.0     # omega (rad/s)
    angular_acceleration: float = 0.0 # alpha (rad/s²)
    radius: float = 0.5

    @property
    def angular_momentum(self) -> float:
        """L = I * omega."""
        return self.moment_of_inertia * self.angular_velocity

    @property
    def rotational_kinetic_energy(self) -> float:
        """KE_rot = ½ * I * omega²."""
        return 0.5 * self.moment_of_inertia * (self.angular_velocity ** 2)


def torque_from_force(
    application_point: Vector2,
    pivot_point: Vector2,
    force: Vector2,
) -> float:
    """Calculate scalar 2D torque: τ = r × F = r_x * F_y - r_y * F_x.

    Args:
        application_point: Point where force is applied.
        pivot_point: Pivot / center of rotation.
        force: Applied force vector.

    Returns:
        Torque in N⋅m (positive = counterclockwise).
    """
    r = application_point - pivot_point
    return r.cross(force)


class RollingBodyOnIncline:
    """Analytical model for a rigid body rolling without slipping down an incline.

    Standard Class 11 NCERT / JEE Problem:
        Acceleration: a = (g * sin θ) / (1 + I / (m * R²))
        Friction force needed for pure rolling: f_s = (m * g * sin θ) / (1 + (m * R²) / I)
        Condition for pure rolling: μ_s >= (tan θ) / (1 + (m * R²) / I)
    """

    def __init__(
        self,
        shape: InertiaShape,
        mass: float,
        radius: float,
        incline_angle_deg: float,
        incline_length: float = 20.0,
        g: float = STANDARD_GRAVITY,
    ) -> None:
        self.shape = shape
        self.mass = mass
        self.radius = radius
        self.theta_deg = incline_angle_deg
        self.theta_rad = math.radians(incline_angle_deg)
        self.length = incline_length
        self.g = g

        self.I = moment_of_inertia(shape, mass, radius)
        # Dimensionless inertia factor beta = I / (m * R²)
        self.beta = self.I / (mass * radius * radius)

    @property
    def acceleration(self) -> float:
        """Linear acceleration down the ramp: a = (g * sin θ) / (1 + β)."""
        return (self.g * math.sin(self.theta_rad)) / (1.0 + self.beta)

    @property
    def angular_acceleration(self) -> float:
        """Angular acceleration: α = a / R."""
        return self.acceleration / self.radius

    @property
    def time_to_bottom(self) -> float:
        """Time to reach the bottom of the ramp: t = √(2L / a)."""
        a = self.acceleration
        if a < 1e-10:
            return 0.0
        return math.sqrt(2.0 * self.length / a)

    @property
    def final_velocity(self) -> float:
        """Velocity at the bottom: v = √(2aL) = √(2gh / (1 + β))."""
        return math.sqrt(2.0 * self.acceleration * self.length)

    @property
    def min_friction_coefficient(self) -> float:
        """Minimum static friction μ_s required to prevent slipping."""
        return math.tan(self.theta_rad) / (1.0 + 1.0 / self.beta)
