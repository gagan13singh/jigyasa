"""Physics validation tests for Fluids & Pulley systems (Class 9 & 11)."""

import pytest

from physengine.mechanics.fluids import terminal_velocity_stokes
from physengine.mechanics.pulley import AtwoodMachine, TablePulleySystem


@pytest.mark.physics
class TestFluidsAndPulleys:
    def test_stokes_terminal_velocity(self):
        """v_t = 2*r²*(rho_p - rho_f)*g / (9*eta)."""
        r = 0.001       # 1 mm sphere
        rho_p = 2500.0  # glass sphere (kg/m³)
        rho_f = 1260.0  # glycerin (kg/m³)
        eta = 1.41      # Pa·s
        g = 9.81

        v_t = terminal_velocity_stokes(
            particle_radius=r,
            particle_density=rho_p,
            fluid_density=rho_f,
            viscosity=eta,
            g=g,
        )

        expected_v_t = (2.0 * (r ** 2) * (rho_p - rho_f) * g) / (9.0 * eta)
        assert abs(v_t - expected_v_t) < 1e-12

    def test_atwood_machine(self):
        """Atwood machine acceleration a = (m1 - m2)/(m1 + m2)*g and string tension."""
        m1, m2 = 3.0, 2.0
        g = 9.81
        atwood = AtwoodMachine(m1=m1, m2=m2, g=g)

        # a = (3 - 2)/5 * 9.81 = 1/5 * 9.81 = 1.962 m/s²
        assert abs(atwood.acceleration - 1.962) < 1e-12
        # T = 2*3*2/5 * 9.81 = 12/5 * 9.81 = 23.544 N
        assert abs(atwood.tension - 23.544) < 1e-12

    def test_table_pulley(self):
        """Table pulley system with friction."""
        m_table = 4.0
        m_hang = 2.0
        mu = 0.2
        g = 9.81
        pulley = TablePulleySystem(
            mass_table=m_table, mass_hanging=m_hang, friction_mu=mu, g=g
        )

        # net driving = (2.0 - 0.2*4.0)*9.81 = (2.0 - 0.8)*9.81 = 1.2 * 9.81
        # a = 1.2 * 9.81 / 6.0 = 0.2 * 9.81 = 1.962 m/s²
        assert abs(pulley.acceleration - 1.962) < 1e-12
