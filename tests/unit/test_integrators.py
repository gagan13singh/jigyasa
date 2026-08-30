"""Unit tests for numerical integrators."""



from physengine.math.vector import Vector2
from physengine.solvers.euler import EulerIntegrator, SemiImplicitEulerIntegrator
from physengine.solvers.rk4 import RK4Integrator
from physengine.solvers.verlet import VelocityVerletIntegrator


class TestEulerIntegrator:
    def test_constant_velocity(self):
        """With zero acceleration, position should advance linearly."""
        integrator = EulerIntegrator()
        pos = Vector2(0, 0)
        vel = Vector2(10, 0)
        acc = Vector2.zero()

        new_pos, new_vel = integrator.step(pos, vel, acc, dt=0.1)
        assert new_pos.close_to(Vector2(1.0, 0))
        assert new_vel.close_to(Vector2(10, 0))

    def test_constant_acceleration(self):
        """With constant acceleration, velocity should increase linearly."""
        integrator = EulerIntegrator()
        pos = Vector2(0, 0)
        vel = Vector2(0, 0)
        acc = Vector2(0, -10)

        new_pos, new_vel = integrator.step(pos, vel, acc, dt=0.1)
        assert new_vel.close_to(Vector2(0, -1.0))
        # Forward Euler: x_new = x + v_old * dt = 0 + 0 * 0.1 = 0
        assert new_pos.close_to(Vector2(0, 0))

    def test_order(self):
        assert EulerIntegrator().order == 1


class TestSemiImplicitEuler:
    def test_constant_acceleration(self):
        """Semi-implicit Euler updates velocity first, then position."""
        integrator = SemiImplicitEulerIntegrator()
        pos = Vector2(0, 0)
        vel = Vector2(0, 0)
        acc = Vector2(0, -10)
        dt = 0.1

        new_pos, new_vel = integrator.step(pos, vel, acc, dt)
        # v_new = 0 + (-10)*0.1 = -1
        assert new_vel.close_to(Vector2(0, -1.0))
        # x_new = 0 + v_new * dt = 0 + (-1)*0.1 = -0.1
        assert new_pos.close_to(Vector2(0, -0.1))

    def test_order(self):
        assert SemiImplicitEulerIntegrator().order == 1


class TestVelocityVerlet:
    def test_constant_acceleration(self):
        """Velocity Verlet should be exact for constant acceleration."""
        integrator = VelocityVerletIntegrator()
        pos = Vector2(0, 10)
        vel = Vector2(0, 0)
        acc = Vector2(0, -10)
        dt = 0.1

        new_pos, new_vel = integrator.step(pos, vel, acc, dt)
        # x_new = 0 + 0*0.1 + 0.5*(-10)*0.01 = -0.05 → y = 10 - 0.05 = 9.95
        assert abs(new_pos.y - 9.95) < 1e-10
        # v_new = 0 + 0.5*(a_old + a_new)*dt = 0 + 0.5*(-10+-10)*0.1 = -1.0
        assert abs(new_vel.y - (-1.0)) < 1e-10

    def test_multiple_steps_accuracy(self):
        """Test Verlet accuracy over many steps against analytical."""
        integrator = VelocityVerletIntegrator()
        pos = Vector2(0, 100)
        vel = Vector2(0, 0)
        g = -9.81
        acc = Vector2(0, g)
        dt = 0.001
        t = 0

        for _ in range(1000):  # 1 second
            new_pos, new_vel = integrator.step(pos, vel, acc, dt)
            pos = new_pos
            vel = new_vel
            t += dt

        # Analytical: y = 100 + 0 - 0.5 * 9.81 * 1² = 100 - 4.905 = 95.095
        expected_y = 100 + 0.5 * g * t * t
        assert abs(pos.y - expected_y) < 0.001  # Less than 1mm error

    def test_order(self):
        assert VelocityVerletIntegrator().order == 2


class TestRK4:
    def test_constant_acceleration(self):
        """RK4 should be exact for constant acceleration (polynomial ≤ degree 4)."""
        integrator = RK4Integrator()
        pos = Vector2(0, 10)
        vel = Vector2(0, 0)
        acc = Vector2(0, -10)
        dt = 0.1

        def acc_fn(p, v):
            return Vector2(0, -10)

        new_pos, new_vel = integrator.step(pos, vel, acc, dt, acc_fn)
        # Analytical: y = 10 - 0.5*10*0.01 = 9.95
        assert abs(new_pos.y - 9.95) < 1e-10

    def test_without_acceleration_fn(self):
        """Without acc_fn, should still work for constant acceleration."""
        integrator = RK4Integrator()
        pos = Vector2(0, 10)
        vel = Vector2(5, 0)
        acc = Vector2(0, -10)
        dt = 0.1

        new_pos, new_vel = integrator.step(pos, vel, acc, dt)
        # x = 0 + 5*0.1 = 0.5
        assert abs(new_pos.x - 0.5) < 1e-10
        # y = 10 - 0.5*10*0.01 = 9.95
        assert abs(new_pos.y - 9.95) < 1e-10

    def test_order(self):
        assert RK4Integrator().order == 4

    def test_higher_accuracy_than_euler(self):
        """RK4 should accumulate less error than Euler over many steps."""
        euler = EulerIntegrator()
        rk4 = RK4Integrator()

        pos = Vector2(0, 100)
        vel = Vector2(10, 20)
        g = -9.81
        acc = Vector2(0, g)
        dt = 0.01

        def acc_fn(p, v):
            return Vector2(0, g)

        pos_e, vel_e = pos, vel
        pos_r, vel_r = pos, vel

        for _ in range(100):  # 1 second
            pos_e, vel_e = euler.step(pos_e, vel_e, acc, dt)
            pos_r, vel_r = rk4.step(pos_r, vel_r, acc, dt, acc_fn)

        # Analytical after 1s
        t = 1.0
        expected_x = 0 + 10 * t
        expected_y = 100 + 20 * t + 0.5 * g * t * t

        euler_error = pos_e.distance_to(Vector2(expected_x, expected_y))
        rk4_error = pos_r.distance_to(Vector2(expected_x, expected_y))

        # RK4 error should be much smaller
        assert rk4_error < euler_error
