"""Physics validation tests for Rotational Dynamics & Incline Rolling (Class 11)."""

import pytest

from physengine.mechanics.rotational import (
    InertiaShape,
    RollingBodyOnIncline,
    moment_of_inertia,
    parallel_axis_theorem,
)


@pytest.mark.physics
class TestRotationalMechanics:
    def test_moments_of_inertia_standard_shapes(self):
        """Verify standard formulas for moments of inertia."""
        m = 2.0
        r = 0.5

        # Solid Sphere: 2/5 m r² = 0.4 * 2.0 * 0.25 = 0.2
        assert abs(moment_of_inertia(InertiaShape.SOLID_SPHERE, m, r) - 0.2) < 1e-12

        # Solid Cylinder (Disk): 1/2 m r² = 0.5 * 2.0 * 0.25 = 0.25
        assert abs(moment_of_inertia(InertiaShape.SOLID_CYLINDER, m, r) - 0.25) < 1e-12

        # Hoop / Ring: 1.0 m r² = 1.0 * 2.0 * 0.25 = 0.5
        assert abs(moment_of_inertia(InertiaShape.HOOP_OR_RING, m, r) - 0.5) < 1e-12

    def test_parallel_axis_theorem(self):
        """I = I_cm + m * d²."""
        I_cm = 10.0
        m = 2.0
        d = 3.0
        # Expected: 10 + 2 * (3²) = 10 + 18 = 28.0
        assert abs(parallel_axis_theorem(I_cm, m, d) - 28.0) < 1e-12

    def test_race_down_inclined_plane(self):
        """Standard Class 11 ranking: Solid Sphere > Solid Cylinder > Hollow Sphere > Ring.

        Acceleration a = (g * sin θ) / (1 + I / (m*R²)).
        Therefore, smaller β gives faster acceleration and shorter time!
        """
        angle = 30.0
        g = 9.81
        m, r = 1.0, 0.2

        sphere = RollingBodyOnIncline(InertiaShape.SOLID_SPHERE, m, r, angle, g=g)
        cylinder = RollingBodyOnIncline(InertiaShape.SOLID_CYLINDER, m, r, angle, g=g)
        hoop = RollingBodyOnIncline(InertiaShape.HOOP_OR_RING, m, r, angle, g=g)

        # Accelerations: Sphere (5/7 g sin θ) > Cylinder (2/3 g sin θ) > Hoop (1/2 g sin θ)
        assert sphere.acceleration > cylinder.acceleration > hoop.acceleration

        # Time to bottom: Sphere arrives first (fastest, smallest time)
        assert sphere.time_to_bottom < cylinder.time_to_bottom < hoop.time_to_bottom
