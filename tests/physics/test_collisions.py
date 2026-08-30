"""Physics validation tests for Collisions and Restitution (Class 11)."""

import pytest

from physengine.mechanics.collisions import (
    BallisticPendulum,
    resolve_collision_1d,
)


@pytest.mark.physics
class TestCollisions1D:
    def test_elastic_equal_masses_swap_velocities(self):
        """Two identical masses in elastic 1D collision swap velocities."""
        v1_init, v2_init = 5.0, -2.0
        v1_final, v2_final = resolve_collision_1d(
            m1=1.0, v1=v1_init, m2=1.0, v2=v2_init, e=1.0
        )
        assert abs(v1_final - v2_init) < 1e-12
        assert abs(v2_final - v1_init) < 1e-12

    def test_elastic_momentum_and_energy_conservation(self):
        """Total momentum and kinetic energy must be conserved in elastic collision."""
        m1, v1 = 2.0, 6.0
        m2, v2 = 3.0, -4.0

        v1_f, v2_f = resolve_collision_1d(m1, v1, m2, v2, e=1.0)

        p_init = m1 * v1 + m2 * v2
        p_final = m1 * v1_f + m2 * v2_f
        assert abs(p_init - p_final) < 1e-12

        ke_init = 0.5 * m1 * v1 * v1 + 0.5 * m2 * v2 * v2
        ke_final = 0.5 * m1 * v1_f * v1_f + 0.5 * m2 * v2_f * v2_f
        assert abs(ke_init - ke_final) < 1e-12

    def test_perfectly_inelastic_collision(self):
        """In perfectly inelastic collision (e=0), bodies move with common velocity."""
        m1, v1 = 2.0, 10.0
        m2, v2 = 3.0, 0.0

        v1_f, v2_f = resolve_collision_1d(m1, v1, m2, v2, e=0.0)

        expected_common_v = (m1 * v1 + m2 * v2) / (m1 + m2)
        assert abs(v1_f - expected_common_v) < 1e-12
        assert abs(v2_f - expected_common_v) < 1e-12


@pytest.mark.physics
class TestBallisticPendulum:
    def test_ballistic_pendulum_analytical(self):
        """Verify bullet embedding speed and maximum height."""
        m_bullet = 0.01  # 10 g
        m_block = 1.99   # 1.99 kg
        v_bullet = 400.0 # 400 m/s
        L = 1.5          # 1.5 m
        g = 9.81

        pendulum = BallisticPendulum(
            bullet_mass=m_bullet,
            block_mass=m_block,
            string_length=L,
            bullet_speed=v_bullet,
            g=g,
        )

        # Expected post-collision velocity: (0.01 * 400) / 2.0 = 2.0 m/s
        assert abs(pendulum.post_collision_speed - 2.0) < 1e-12

        # Expected max height: v² / (2g) = 4 / (2 * 9.81) = 0.20387 m
        expected_h = (2.0 ** 2) / (2.0 * g)
        assert abs(pendulum.max_height - expected_h) < 1e-12
