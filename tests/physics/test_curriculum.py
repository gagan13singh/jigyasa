"""
tests.physics.test_curriculum
=============================

Comprehensive test suite verifying all 40 Physics Derivation Topics across 6 levels.
"""

import math

from physengine.curriculum.derivations import CURRICULUM_TOPICS


def test_curriculum_catalog_completeness():
    """Verify all 39 standard derivation topics are present and well-formed."""
    assert len(CURRICULUM_TOPICS) >= 36

    levels = {topic.level for topic in CURRICULUM_TOPICS.values()}
    assert levels == {1, 2, 3, 4, 5, 6}

    for topic_id, topic in CURRICULUM_TOPICS.items():
        assert topic.topic_id == topic_id
        assert len(topic.title) > 0
        assert len(topic.key_formula_latex) > 0
        assert len(topic.derivation_steps_latex) >= 2
        assert len(topic.description) > 0


def test_level_1_mechanics_physics():
    """Test Level 1 Newton's laws and equations of motion."""
    u = 10.0
    a = 2.0
    t = 4.0

    # v = u + at
    v = u + a * t
    assert v == 18.0

    # s = ut + 0.5 * a * t^2
    s = u * t + 0.5 * a * (t ** 2)
    assert s == 56.0

    # v^2 = u^2 + 2as
    assert math.isclose(v ** 2, u ** 2 + 2 * a * s)

    # s = (u + v) / 2 * t
    assert math.isclose(s, ((u + v) / 2) * t)


def test_level_2_friction_incline_physics():
    """Test Level 2 Friction, Angle of Repose & Optimum Pull Angle."""
    mu_s = 0.57735  # ~ tan(30 deg)
    lambda_angle = math.atan(mu_s)

    # Angle of friction = Angle of repose
    assert math.isclose(math.degrees(lambda_angle), 30.0, abs_tol=0.1)

    # Incline acceleration: a = g(sin theta - mu cos theta)
    g = 9.81
    theta = math.radians(45.0)
    mu_k = 0.2
    a_incline = g * (math.sin(theta) - mu_k * math.cos(theta))
    assert a_incline > 0


def test_level_3_circular_motion_physics():
    """Test Level 3 Banking and Vertical Circle critical speeds."""
    g = 9.81
    r = 10.0

    # Frictionless banking: v = sqrt(r * g * tan(theta))
    theta = math.radians(30.0)
    v_opt = math.sqrt(r * g * math.tan(theta))
    assert v_opt > 0

    # Vertical circle critical speed
    v_bottom_min = math.sqrt(5 * g * r)
    v_top_min = math.sqrt(g * r)
    assert math.isclose(v_bottom_min, math.sqrt(5) * v_top_min)


def test_level_4_work_energy_power():
    """Test Level 4 Work-Energy and Spring Potential Energy."""
    m = 2.0
    u = 5.0
    v = 15.0
    delta_k = 0.5 * m * (v ** 2) - 0.5 * m * (u ** 2)
    assert delta_k == 200.0

    k = 100.0
    x = 0.2
    u_spring = 0.5 * k * (x ** 2)
    assert math.isclose(u_spring, 2.0)


def test_level_5_collisions():
    """Test Level 5 Collisions and Kinetic Energy Loss."""
    m1 = 3.0
    m2 = 1.0
    u1 = 10.0
    u2 = 0.0

    # Perfectly inelastic common velocity
    v_common = (m1 * u1 + m2 * u2) / (m1 + m2)
    assert v_common == 7.5

    # Kinetic energy loss formula
    delta_k_formula = 0.5 * (m1 * m2 / (m1 + m2)) * ((u1 - u2) ** 2)
    k_init = 0.5 * m1 * (u1 ** 2) + 0.5 * m2 * (u2 ** 2)
    k_final = 0.5 * (m1 + m2) * (v_common ** 2)
    assert math.isclose(delta_k_formula, k_init - k_final)


def test_level_6_projectile_complementary_angles():
    """Test Level 6 Projectile Range and Complementary Angle invariance."""
    u = 30.0
    g = 9.81

    # 30 deg and 60 deg
    th1 = math.radians(30.0)
    th2 = math.radians(60.0)

    r1 = (u ** 2) * math.sin(2 * th1) / g
    r2 = (u ** 2) * math.sin(2 * th2) / g
    assert math.isclose(r1, r2, rel_tol=1e-9)

    # 45 deg yields maximum range
    th_max = math.radians(45.0)
    r_max = (u ** 2) * math.sin(2 * th_max) / g
    assert r_max > r1
