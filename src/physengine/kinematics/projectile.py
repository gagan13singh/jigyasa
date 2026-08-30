"""
physengine.kinematics.projectile
================================

Analytical solution for projectile motion (no air resistance).

This provides exact, closed-form answers for the standard projectile
problem — extremely useful for:
1. Validating numerical simulations
2. Quick calculations in Scientia/Vidyastra
3. Generating reference trajectories

All calculations assume:
- Uniform gravitational field (constant g downward)
- No air resistance
- Flat ground at y = launch_height (or y = 0 by default)
"""

from __future__ import annotations

import math

from physengine.math.constants import STANDARD_GRAVITY
from physengine.math.vector import Vector2


class ProjectileMotion:
    """Complete analytical solution for ideal projectile motion.

    Given initial conditions, computes every property of the trajectory
    without simulation.

    Usage:
        >>> proj = ProjectileMotion(v0=20, angle=45, g=9.81, height=0)
        >>> proj.range          # 40.77...
        >>> proj.max_height     # 10.19...
        >>> proj.time_of_flight # 2.886...
        >>> proj.position_at(1.0)  # Vector2(14.14, 9.24)
    """

    def __init__(
        self,
        v0: float,
        angle: float,
        g: float = STANDARD_GRAVITY,
        height: float = 0.0,
    ) -> None:
        """
        Args:
            v0: Initial speed (m/s).
            angle: Launch angle in **degrees** from horizontal.
            g: Gravitational acceleration magnitude (m/s²).
            height: Launch height above ground (m).
        """
        self.v0 = v0
        self.angle_deg = angle
        self.angle_rad = math.radians(angle)
        self.g = g
        self.height = height

        # Decomposed initial velocity
        self.vx0 = v0 * math.cos(self.angle_rad)
        self.vy0 = v0 * math.sin(self.angle_rad)

    # -- Core trajectory functions -------------------------------------------
    def position_at(self, t: float) -> Vector2:
        """Position at time t.

        x(t) = vx₀ * t
        y(t) = h + vy₀ * t - ½gt²
        """
        x = self.vx0 * t
        y = self.height + self.vy0 * t - 0.5 * self.g * t * t
        return Vector2(x, y)

    def velocity_at(self, t: float) -> Vector2:
        """Velocity at time t.

        vx(t) = vx₀
        vy(t) = vy₀ - gt
        """
        return Vector2(self.vx0, self.vy0 - self.g * t)

    def speed_at(self, t: float) -> float:
        """Scalar speed at time t."""
        return self.velocity_at(t).magnitude

    def acceleration_at(self, t: float) -> Vector2:
        """Acceleration at time t (constant)."""
        return Vector2(0.0, -self.g)

    # -- Key properties ------------------------------------------------------
    @property
    def time_of_flight(self) -> float:
        """Total time until the projectile returns to ground level (y = 0).

        Solves: h + vy₀*t - ½gt² = 0 for the positive root.

        Uses quadratic formula:
            t = (vy₀ + √(vy₀² + 2gh)) / g
        """
        discriminant = self.vy0 * self.vy0 + 2.0 * self.g * self.height
        if discriminant < 0:
            return 0.0
        return (self.vy0 + math.sqrt(discriminant)) / self.g

    @property
    def max_height(self) -> float:
        """Maximum height above ground.

        Occurs when vy = 0, at t = vy₀/g.
        y_max = h + vy₀²/(2g)
        """
        return self.height + self.vy0 * self.vy0 / (2.0 * self.g)

    @property
    def time_to_max_height(self) -> float:
        """Time to reach maximum height: t = vy₀/g."""
        return self.vy0 / self.g

    @property
    def range(self) -> float:
        """Horizontal distance at landing (y = 0).

        R = vx₀ * t_flight
        """
        return self.vx0 * self.time_of_flight

    @property
    def impact_velocity(self) -> Vector2:
        """Velocity at the moment of landing."""
        return self.velocity_at(self.time_of_flight)

    @property
    def impact_speed(self) -> float:
        """Speed at the moment of landing."""
        return self.impact_velocity.magnitude

    @property
    def impact_angle(self) -> float:
        """Angle of impact below horizontal (degrees)."""
        v = self.impact_velocity
        return math.degrees(math.atan2(-v.y, v.x))

    # -- Trajectory generation -----------------------------------------------
    def trajectory(self, num_points: int = 100) -> list[Vector2]:
        """Generate evenly-spaced points along the trajectory.

        Args:
            num_points: Number of points to generate.

        Returns:
            List of position Vector2s from launch to landing.
        """
        t_flight = self.time_of_flight
        points: list[Vector2] = []
        for i in range(num_points + 1):
            t = t_flight * i / num_points
            points.append(self.position_at(t))
        return points

    def trajectory_with_time(
        self, num_points: int = 100
    ) -> list[tuple[float, Vector2]]:
        """Generate trajectory with timestamps.

        Returns:
            List of (time, position) tuples.
        """
        t_flight = self.time_of_flight
        result: list[tuple[float, Vector2]] = []
        for i in range(num_points + 1):
            t = t_flight * i / num_points
            result.append((t, self.position_at(t)))
        return result

    # -- Equation of trajectory (y as a function of x) -----------------------
    def y_at_x(self, x: float) -> float:
        """Height at horizontal distance x.

        y(x) = h + x*tan(θ) - (g*x²)/(2*vx₀²)
        """
        if abs(self.vx0) < 1e-15:
            return self.height
        return (
            self.height
            + x * math.tan(self.angle_rad)
            - (self.g * x * x) / (2.0 * self.vx0 * self.vx0)
        )

    # -- Display -------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"ProjectileMotion(v0={self.v0:.4g} m/s, "
            f"angle={self.angle_deg:.1f} deg, "
            f"g={self.g:.4g} m/s^2, "
            f"h={self.height:.4g} m)"
        )

    def summary(self) -> str:
        """Human-readable summary of projectile properties."""
        return (
            f"Projectile Motion Summary\n"
            f"{'-' * 40}\n"
            f"Initial speed:     {self.v0:.4f} m/s\n"
            f"Launch angle:      {self.angle_deg:.1f} deg\n"
            f"Launch height:     {self.height:.4f} m\n"
            f"Gravity:           {self.g:.4f} m/s^2\n"
            f"{'-' * 40}\n"
            f"Horizontal vel:    {self.vx0:.4f} m/s\n"
            f"Vertical vel:      {self.vy0:.4f} m/s\n"
            f"Time of flight:    {self.time_of_flight:.4f} s\n"
            f"Range:             {self.range:.4f} m\n"
            f"Max height:        {self.max_height:.4f} m\n"
            f"Time to apex:      {self.time_to_max_height:.4f} s\n"
            f"Impact speed:      {self.impact_speed:.4f} m/s\n"
            f"Impact angle:      {self.impact_angle:.1f} deg below horizontal\n"
        )


# -- Convenience functions ---------------------------------------------------
def optimal_angle_for_range(v0: float, g: float = STANDARD_GRAVITY) -> float:
    """Optimal launch angle for maximum range (from ground level).

    Returns:
        45 degrees (for flat ground, no air resistance).
    """
    return 45.0


def max_range(v0: float, g: float = STANDARD_GRAVITY) -> float:
    """Maximum horizontal range (from ground level, no air resistance).

    R_max = v₀² / g  (at 45°)
    """
    return v0 * v0 / g


def range_at_angle(
    v0: float, angle_deg: float, g: float = STANDARD_GRAVITY
) -> float:
    """Horizontal range at a given launch angle (from ground level).

    R = (v₀² * sin(2θ)) / g
    """
    angle_rad = math.radians(angle_deg)
    return v0 * v0 * math.sin(2 * angle_rad) / g
