"""
physengine.scientia.solver
==========================

Deterministic Physics Model Solver & Simulation Generator for Scientia DPA.
Converts structured ProblemSpec representations into:
1. Verified Step-by-Step Mathematical Solutions (LaTeX)
2. Free-Body Diagram (FBD) Force Vector Models
3. High-Precision Numerical Simulation Time-Series Snapshots
"""

from __future__ import annotations

import math
from typing import Any

from physengine.core.config import SimulationConfig
from physengine.core.simulation import Simulation
from physengine.core.world import World
from physengine.math.vector import Vector2
from physengine.mechanics.forces import ConstantForce
from physengine.mechanics.particle import Particle
from physengine.scientia.schema import (
    DPASolution,
    DPASolutionStep,
    FBDVectorSpec,
    ProblemSpec,
    SystemType,
)


class ProblemSolver:
    """Solves structured physics problems and generates coupled simulations."""

    def solve(self, problem: ProblemSpec) -> DPASolution:
        """Route to appropriate system solver based on problem specification."""
        if problem.system_type == SystemType.BLOCK_HORIZONTAL:
            return self._solve_block_horizontal(problem)
        elif problem.system_type == SystemType.BLOCK_INCLINE:
            return self._solve_block_incline(problem)
        elif problem.system_type == SystemType.PROJECTILE:
            return self._solve_projectile(problem)
        elif problem.system_type == SystemType.CIRCULAR_BANKING:
            return self._solve_circular_banking(problem)
        elif problem.system_type == SystemType.SPRING_MASS:
            return self._solve_spring_mass(problem)
        elif problem.system_type == SystemType.COLLISION_1D:
            return self._solve_collision_1d(problem)
        elif problem.system_type == SystemType.TWO_BODY_PULLEY:
            return self._solve_two_body_pulley(problem)
        else:
            return self._solve_block_horizontal(problem)

    def _solve_block_horizontal(self, problem: ProblemSpec) -> DPASolution:
        """Solve a block on a horizontal rough surface with applied force."""
        m = problem.parameters.get("mass", 5.0)
        F_app = problem.parameters.get("applied_force", 20.0)
        mu = problem.parameters.get("mu", 0.2)
        g = problem.parameters.get("g", 9.81)
        pull_angle_deg = problem.parameters.get("pull_angle_deg", 0.0)
        pull_rad = math.radians(pull_angle_deg)

        # 1. Normal force: N = mg - F*sin(theta)
        N = max(0.0, m * g - F_app * math.sin(pull_rad))

        # 2. Maximum static / kinetic friction force: f_k = mu * N
        f_k = mu * N

        # 3. Net horizontal force: F_net = F*cos(theta) - f_k
        F_h = F_app * math.cos(pull_rad)
        is_moving = F_h > f_k
        F_net = max(0.0, F_h - f_k) if is_moving else 0.0

        # 4. Acceleration: a = F_net / m
        a = F_net / m if is_moving else 0.0

        # Build Pedagogical Solution Steps
        steps = [
            DPASolutionStep(
                step_number=1,
                title="Identify System & Given Parameters",
                latex_formula=rf"m = {m}\,\text{{kg}}, \quad F = {F_app}\,\text{{N}}, \quad \mu = {mu}, \quad g = {g}\,\text{{m/s}}^2",
                description="List all given kinematic and dynamic quantities from problem statement.",
                values={"mass": m, "applied_force": F_app, "mu": mu, "g": g},
            ),
            DPASolutionStep(
                step_number=2,
                title="Vertical Equilibrium & Normal Reaction",
                latex_formula=rf"N = mg - F\sin\theta = ({m})({g}) - {F_app}\sin({pull_angle_deg}^\circ) = {N:.2f}\,\text{{N}}",
                description="Equate vertical forces to find the normal contact force exerted by the ground.",
                values={"N": round(N, 3)},
            ),
            DPASolutionStep(
                step_number=3,
                title="Calculate Friction Force",
                latex_formula=rf"f = \mu N = ({mu})({N:.2f}) = {f_k:.2f}\,\text{{N}}",
                description="Compute the opposing friction force along the contact interface.",
                values={"friction": round(f_k, 3)},
            ),
            DPASolutionStep(
                step_number=4,
                title="Apply Newton's Second Law along Horizontal Axis",
                latex_formula=rf"F_{{\text{{net}}}} = F\cos\theta - f = {F_h:.2f} - {f_k:.2f} = {F_net:.2f}\,\text{{N}}",
                description="Subtract friction from applied horizontal force component to determine net driving force.",
                values={"F_net": round(F_net, 3)},
            ),
            DPASolutionStep(
                step_number=5,
                title="Calculate Acceleration",
                latex_formula=rf"a = \frac{{F_{{\text{{net}}}}}}{{m}} = \frac{{{F_net:.2f}}}{{{m}}} = \mathbf{{{a:.3f}\,\text{{m/s}}^2}}",
                description="Divide net force by inertia (mass) to solve for resulting linear acceleration.",
                values={"acceleration": round(a, 3)},
            ),
        ]

        # Free Body Diagram Vectors
        fbd_vectors = [
            FBDVectorSpec(
                "Applied Force",
                r"\vec{F}",
                F_app,
                (0.0, 0.0),
                (math.cos(pull_rad), math.sin(pull_rad)),
                "#38bdf8",
            ),
            FBDVectorSpec("Normal Force", r"\vec{N}", N, (0.0, 0.0), (0.0, 1.0), "#10b981"),
            FBDVectorSpec("Gravity", r"m\vec{g}", m * g, (0.0, 0.0), (0.0, -1.0), "#ef4444"),
            FBDVectorSpec("Friction", r"\vec{f}_k", f_k, (0.0, 0.0), (-1.0, 0.0), "#f59e0b"),
        ]

        # Run Real Simulation via PhysEngine Core Kernel
        world = World(gravity=0.0)  # we handle contact normal & friction
        block = Particle(mass=m, position=(0.0, 0.0), name="block")
        world.add(block)
        if is_moving:
            world.add_force(ConstantForce(Vector2(F_net, 0.0)))

        sim = Simulation(world, config=SimulationConfig(timestep=1.0 / 60.0))
        sim.run(duration=4.0)

        # Extract timeline frames
        timeline: list[dict[str, Any]] = []
        for state in sim.history.snapshots:
            entity = state.get_entity("block")
            pos = entity.position
            vel = entity.velocity
            v_mag = vel.magnitude
            timeline.append(
                {
                    "t": state.time,
                    "entities": {
                        "block": {
                            "name": f"Block ({m:.1f}kg)",
                            "x": pos.x,
                            "y": pos.y,
                            "vx": vel.x,
                            "vy": vel.y,
                            "ax": a,
                            "ay": 0.0,
                            "speed": v_mag,
                            "ke": entity.kinetic_energy,
                        }
                    },
                    "telemetry": {
                        "F_net": F_net,
                        "N": N,
                        "f_friction": f_k,
                        "acceleration": a,
                    },
                }
            )

        return DPASolution(
            problem_id=problem.problem_id,
            system_type="block_horizontal",
            target_unknown=problem.target_unknown,
            answer_value=round(a, 3),
            answer_unit="m/s²",
            answer_latex=rf"a = {a:.3f}\,\text{{m/s}}^2",
            steps=steps,
            fbd_vectors=fbd_vectors,
            numerical_results={
                "acceleration": a,
                "normal_force": N,
                "friction_force": f_k,
                "net_force": F_net,
            },
            simulation_timeline=timeline,
            concepts_used=[
                "newton_second_law",
                "static_friction",
                "kinetic_friction",
                "fbd",
                "normal_reaction",
            ],
        )

    def _solve_block_incline(self, problem: ProblemSpec) -> DPASolution:
        """Solve block sliding down a rough inclined plane."""
        m = problem.parameters.get("mass", 2.0)
        theta_deg = problem.parameters.get("incline_deg", 30.0)
        mu = problem.parameters.get("mu", 0.2)
        g = problem.parameters.get("g", 9.81)
        th = math.radians(theta_deg)

        # 1. Normal force: N = mg*cos(theta)
        N = m * g * math.cos(th)

        # 2. Friction force: f_k = mu * N = mu * mg * cos(theta)
        f_k = mu * N

        # 3. Driving gravitational component down plane: F_parallel = mg*sin(theta)
        F_parallel = m * g * math.sin(th)

        # 4. Net acceleration down plane: a = g*(sin(theta) - mu*cos(theta))
        a = max(0.0, g * (math.sin(th) - mu * math.cos(th)))

        steps = [
            DPASolutionStep(
                step_number=1,
                title="Decompose Gravitational Force onto Incline Axes",
                latex_formula=rf"F_\parallel = mg\sin\theta = ({m})({g})\sin({theta_deg}^\circ) = {F_parallel:.2f}\,\text{{N}}, \quad N = mg\cos\theta = {N:.2f}\,\text{{N}}",
                description="Resolve weight into components parallel and perpendicular to the inclined plane.",
                values={"F_parallel": round(F_parallel, 3), "N": round(N, 3)},
            ),
            DPASolutionStep(
                step_number=2,
                title="Calculate Opposing Kinetic Friction",
                latex_formula=rf"f_k = \mu_k N = ({mu})({N:.2f}) = {f_k:.2f}\,\text{{N}}",
                description="Determine the maximum friction force opposing motion up the slope.",
                values={"f_k": round(f_k, 3)},
            ),
            DPASolutionStep(
                step_number=3,
                title="Apply Newton's Second Law along Incline",
                latex_formula=rf"F_{{\text{{net}}}} = mg\sin\theta - f_k = {F_parallel:.2f} - {f_k:.2f} = {F_parallel - f_k:.2f}\,\text{{N}}",
                description="Subtract friction from the downhill gravitational component.",
                values={"F_net": round(F_parallel - f_k, 3)},
            ),
            DPASolutionStep(
                step_number=4,
                title="Compute Incline Acceleration",
                latex_formula=rf"a = g(\sin\theta - \mu_k\cos\theta) = \mathbf{{{a:.3f}\,\text{{m/s}}^2}}",
                description="Resulting acceleration of the block sliding down the plane.",
                values={"acceleration": round(a, 3)},
            ),
        ]

        fbd_vectors = [
            FBDVectorSpec(
                "Normal Force", r"\vec{N}", N, (0.0, 0.0), (-math.sin(th), math.cos(th)), "#10b981"
            ),
            FBDVectorSpec("Gravity", r"m\vec{g}", m * g, (0.0, 0.0), (0.0, -1.0), "#ef4444"),
            FBDVectorSpec(
                "Friction", r"\vec{f}_k", f_k, (0.0, 0.0), (-math.cos(th), -math.sin(th)), "#f59e0b"
            ),
        ]

        # Generate timeline
        ramp_len = 22.0
        s0 = 2.0
        dt = 1.0 / 60.0
        total_steps = int(4.0 / dt)
        timeline = []
        for i in range(total_steps + 1):
            t = i * dt
            s_travel = 0.5 * a * t * t
            s_curr = min(ramp_len, s0 + s_travel)
            x = s_curr * math.cos(th)
            y = (ramp_len - s_curr) * math.sin(th)
            v_curr = a * t
            timeline.append(
                {
                    "t": t,
                    "inclineAngle": th,
                    "entities": {
                        "block": {
                            "name": "Incline Block",
                            "x": x,
                            "y": y,
                            "vx": v_curr * math.cos(th),
                            "vy": -v_curr * math.sin(th),
                            "ax": a * math.cos(th),
                            "ay": -a * math.sin(th),
                            "speed": v_curr,
                            "ke": 0.5 * m * v_curr * v_curr,
                            "inclineAngle": th,
                        }
                    },
                    "telemetry": {"acceleration": a, "N": N, "f_friction": f_k},
                }
            )

        return DPASolution(
            problem_id=problem.problem_id,
            system_type="block_incline",
            target_unknown=problem.target_unknown,
            answer_value=round(a, 3),
            answer_unit="m/s²",
            answer_latex=rf"a = {a:.3f}\,\text{{m/s}}^2",
            steps=steps,
            fbd_vectors=fbd_vectors,
            numerical_results={"acceleration": a, "normal_force": N, "friction_force": f_k},
            simulation_timeline=timeline,
            concepts_used=[
                "inclined_plane",
                "static_friction",
                "kinetic_friction",
                "newton_second_law",
            ],
        )

    def _solve_projectile(self, problem: ProblemSpec) -> DPASolution:
        """Solve 2D parabolic projectile motion."""
        u = problem.parameters.get("velocity", 20.0)
        theta_deg = problem.parameters.get("angle", 45.0)
        g = problem.parameters.get("g", 9.81)
        m = problem.parameters.get("mass", 1.0)
        th = math.radians(theta_deg)

        # Kinematic metrics
        t_apex = (u * math.sin(th)) / g
        T_flight = 2.0 * t_apex
        H_max = (u * u * (math.sin(th) ** 2)) / (2.0 * g)
        R_range = (u * u * math.sin(2.0 * th)) / g

        steps = [
            DPASolutionStep(
                step_number=1,
                title="Decompose Initial Velocity Components",
                latex_formula=rf"u_x = u\cos\theta = {u}\cos({theta_deg}^\circ) = {u * math.cos(th):.2f}\,\text{{m/s}}, \quad u_y = u\sin\theta = {u * math.sin(th):.2f}\,\text{{m/s}}",
                description="Split initial velocity vector into independent orthogonal axes.",
                values={"ux": round(u * math.cos(th), 3), "uy": round(u * math.sin(th), 3)},
            ),
            DPASolutionStep(
                step_number=2,
                title="Calculate Time of Flight",
                latex_formula=rf"T = \frac{{2u\sin\theta}}{{g}} = \frac{{2({u})\sin({theta_deg}^\circ)}}{{{g}}} = \mathbf{{{T_flight:.3f}\,\text{{s}}}}",
                description="Total elapsed time before projectile impacts the ground level y = 0.",
                values={"flight_time": round(T_flight, 3)},
            ),
            DPASolutionStep(
                step_number=3,
                title="Calculate Maximum Height",
                latex_formula=rf"H_{{\max}} = \frac{{u^2\sin^2\theta}}{{2g}} = \frac{{{u}^2\sin^2({theta_deg}^\circ)}}{{2({g})}} = \mathbf{{{H_max:.2f}\,\text{{m}}}}",
                description="Vertical peak altitude where vertical velocity component vy momentarily vanishes.",
                values={"max_height": round(H_max, 3)},
            ),
            DPASolutionStep(
                step_number=4,
                title="Calculate Horizontal Range",
                latex_formula=rf"R = \frac{{u^2\sin 2\theta}}{{g}} = \frac{{{u}^2\sin({2 * theta_deg}^\circ)}}{{{g}}} = \mathbf{{{R_range:.2f}\,\text{{m}}}}",
                description="Total horizontal ground distance spanned from launch to landing.",
                values={"range": round(R_range, 3)},
            ),
        ]

        fbd_vectors = [
            FBDVectorSpec("Gravity", r"m\vec{g}", m * g, (0.0, 0.0), (0.0, -1.0), "#ef4444"),
        ]

        dt = 1.0 / 60.0
        total_steps = int(T_flight / dt)
        timeline = []
        for i in range(total_steps + 1):
            t = i * dt
            x = u * math.cos(th) * t
            y = max(0.0, u * math.sin(th) * t - 0.5 * g * t * t)
            vx = u * math.cos(th)
            vy = u * math.sin(th) - g * t
            speed = math.hypot(vx, vy)
            timeline.append(
                {
                    "t": t,
                    "entities": {
                        "projectile": {
                            "name": "Projectile",
                            "x": x,
                            "y": y,
                            "vx": vx,
                            "vy": vy,
                            "ax": 0.0,
                            "ay": -g,
                            "speed": speed,
                            "ke": 0.5 * m * speed * speed,
                        }
                    },
                    "telemetry": {"range": R_range, "H_max": H_max, "T_flight": T_flight},
                }
            )

        return DPASolution(
            problem_id=problem.problem_id,
            system_type="projectile",
            target_unknown=problem.target_unknown,
            answer_value=round(R_range, 3),
            answer_unit="m",
            answer_latex=rf"R = {R_range:.2f}\,\text{{m}}",
            steps=steps,
            fbd_vectors=fbd_vectors,
            numerical_results={"range": R_range, "max_height": H_max, "flight_time": T_flight},
            simulation_timeline=timeline,
            concepts_used=[
                "projectile_motion",
                "parabolic_trajectory",
                "range",
                "equations_of_motion",
            ],
        )

    def _solve_circular_banking(self, problem: ProblemSpec) -> DPASolution:
        """Solve road banking with friction and safe velocity envelope."""
        R = problem.parameters.get("radius", 10.0)
        theta_deg = problem.parameters.get("incline_deg", 25.0)
        mu = problem.parameters.get("mu", 0.3)
        g = problem.parameters.get("g", 9.81)
        m = problem.parameters.get("mass", 1000.0)
        th = math.radians(theta_deg)
        tan_th = math.tan(th)

        # 1. Optimum design speed: v_opt = sqrt(R*g*tan(theta))
        v_opt = math.sqrt(R * g * tan_th)

        # 2. Maximum safe speed: v_max
        denom_max = 1.0 - mu * tan_th
        v_max = math.sqrt(R * g * ((tan_th + mu) / denom_max)) if denom_max > 0.001 else 999.0

        # 3. Minimum safe speed: v_min
        num_min = tan_th - mu
        v_min = math.sqrt(R * g * (num_min / (1.0 + mu * tan_th))) if num_min > 0.001 else 0.0

        steps = [
            DPASolutionStep(
                step_number=1,
                title="Calculate Optimum Frictionless Design Speed",
                latex_formula=rf"v_{{\text{{opt}}}} = \sqrt{{Rg\tan\theta}} = \sqrt{{({R})({g})\tan({theta_deg}^\circ)}} = \mathbf{{{v_opt:.2f}\,\text{{m/s}}}}",
                description="Speed at which horizontal normal component supplies 100% of centripetal force with zero friction.",
                values={"v_opt": round(v_opt, 3)},
            ),
            DPASolutionStep(
                step_number=2,
                title="Calculate Maximum Safe Speed before Outward Skid",
                latex_formula=rf"v_{{\max}} = \sqrt{{Rg\left(\frac{{\tan\theta + \mu}}{{1 - \mu\tan\theta}}\right)}} = \mathbf{{{v_max:.2f}\,\text{{m/s}}}}",
                description="Upper velocity limit where limiting static friction acts down the incline.",
                values={"v_max": round(v_max, 3)},
            ),
            DPASolutionStep(
                step_number=3,
                title="Calculate Minimum Safe Speed to Prevent Inward Slip",
                latex_formula=rf"v_{{\min}} = \sqrt{{Rg\left(\frac{{\tan\theta - \mu}}{{1 + \mu\tan\theta}}\right)}} = \mathbf{{{v_min:.2f}\,\text{{m/s}}}}",
                description="Lower velocity limit where limiting static friction acts up the incline.",
                values={"v_min": round(v_min, 3)},
            ),
        ]

        fbd_vectors = [
            FBDVectorSpec(
                "Normal Force",
                r"\vec{N}",
                m * g / math.cos(th),
                (0.0, 0.0),
                (-math.sin(th), math.cos(th)),
                "#10b981",
            ),
            FBDVectorSpec("Gravity", r"m\vec{g}", m * g, (0.0, 0.0), (0.0, -1.0), "#ef4444"),
        ]

        return DPASolution(
            problem_id=problem.problem_id,
            system_type="circular_banking",
            target_unknown=problem.target_unknown,
            answer_value=round(v_opt, 3),
            answer_unit="m/s",
            answer_latex=rf"v_{{\text{{opt}}}} = {v_opt:.2f}\,\text{{m/s}}, \quad [v_{{\min}}, v_{{\max}}] = [{v_min:.2f}, {v_max:.2f}]",
            steps=steps,
            fbd_vectors=fbd_vectors,
            numerical_results={"v_opt": v_opt, "v_max": v_max, "v_min": v_min},
            simulation_timeline=[],
            concepts_used=["banking_with_friction", "centripetal_force", "circular_motion"],
        )

    def _solve_spring_mass(self, problem: ProblemSpec) -> DPASolution:
        """Solve spring-mass simple harmonic oscillator."""
        m = problem.parameters.get("mass", 2.0)
        k = problem.parameters.get("k", 50.0)
        A = problem.parameters.get("amplitude", 0.5)

        omega = math.sqrt(k / m)
        T_period = (2.0 * math.pi) / omega
        E_tot = 0.5 * k * A * A
        v_max = A * omega

        steps = [
            DPASolutionStep(
                step_number=1,
                title="Calculate Angular Frequency",
                latex_formula=rf"\omega = \sqrt{{\frac{{k}}{{m}}}} = \sqrt{{\frac{{{k}}}{{{m}}}}} = {omega:.3f}\,\text{{rad/s}}",
                description="Natural frequency of vibration determined by stiffness and inertia.",
                values={"omega": round(omega, 3)},
            ),
            DPASolutionStep(
                step_number=2,
                title="Calculate Time Period of Oscillation",
                latex_formula=rf"T = 2\pi\sqrt{{\frac{{m}}{{k}}}} = \frac{{2\pi}}{{{omega:.3f}}} = \mathbf{{{T_period:.3f}\,\text{{s}}}}",
                description="Time required to complete one full back-and-forth cycle.",
                values={"period": round(T_period, 3)},
            ),
            DPASolutionStep(
                step_number=3,
                title="Calculate Total Mechanical Energy",
                latex_formula=rf"E = \frac{{1}}{{2}}kA^2 = \frac{{1}}{{2}}({k})({A})^2 = \mathbf{{{E_tot:.3f}\,\text{{J}}}}",
                description="Constant total energy interchanging between kinetic and elastic potential.",
                values={"total_energy": round(E_tot, 3), "v_max": round(v_max, 3)},
            ),
        ]

        fbd_vectors = [
            FBDVectorSpec(
                "Restoring Force", r"\vec{F}_s = -kx", k * A, (0.0, 0.0), (-1.0, 0.0), "#38bdf8"
            ),
        ]

        return DPASolution(
            problem_id=problem.problem_id,
            system_type="spring_mass",
            target_unknown=problem.target_unknown,
            answer_value=round(T_period, 3),
            answer_unit="s",
            answer_latex=rf"T = {T_period:.3f}\,\text{{s}}",
            steps=steps,
            fbd_vectors=fbd_vectors,
            numerical_results={
                "period": T_period,
                "omega": omega,
                "total_energy": E_tot,
                "v_max": v_max,
            },
            simulation_timeline=[],
            concepts_used=["spring_potential_energy", "hooke_law", "shm", "conservation_of_energy"],
        )

    def _solve_collision_1d(self, problem: ProblemSpec) -> DPASolution:
        """Solve 1D collision with restitution coefficient e."""
        m1 = problem.parameters.get("m1", 2.0)
        m2 = problem.parameters.get("m2", 3.0)
        u1 = problem.parameters.get("u1", 5.0)
        u2 = problem.parameters.get("u2", -2.0)
        e = problem.parameters.get("e", 1.0)

        v1 = (m1 * u1 + m2 * u2 - m2 * e * (u1 - u2)) / (m1 + m2)
        v2 = (m1 * u1 + m2 * u2 + m1 * e * (u1 - u2)) / (m1 + m2)

        steps = [
            DPASolutionStep(
                step_number=1,
                title="Apply Conservation of Linear Momentum",
                latex_formula=rf"m_1 u_1 + m_2 u_2 = ({m1})({u1}) + ({m2})({u2}) = {m1 * u1 + m2 * u2:.2f}\,\text{{kg}}\cdot\text{{m/s}}",
                description="Total linear momentum remains constant before and after impact.",
                values={"total_p": round(m1 * u1 + m2 * u2, 3)},
            ),
            DPASolutionStep(
                step_number=2,
                title="Apply Coefficient of Restitution Definition",
                latex_formula=rf"e = \frac{{v_2 - v_1}}{{u_1 - u_2}} = {e:.2f} \implies v_2 - v_1 = {e * (u1 - u2):.2f}\,\text{{m/s}}",
                description="Relates velocity of separation to velocity of approach.",
                values={"v_rel": round(e * (u1 - u2), 3)},
            ),
            DPASolutionStep(
                step_number=3,
                title="Solve for Final Velocities",
                latex_formula=rf"v_1 = \mathbf{{{v1:.3f}\,\text{{m/s}}}}, \quad v_2 = \mathbf{{{v2:.3f}\,\text{{m/s}}}}",
                description="Individual post-collision velocities after impact.",
                values={"v1": round(v1, 3), "v2": round(v2, 3)},
            ),
        ]

        fbd_vectors = []

        return DPASolution(
            problem_id=problem.problem_id,
            system_type="collision_1d",
            target_unknown=problem.target_unknown,
            answer_value=round(v1, 3),
            answer_unit="m/s",
            answer_latex=rf"v_1 = {v1:.3f}\,\text{{m/s}}, \quad v_2 = {v2:.3f}\,\text{{m/s}}",
            steps=steps,
            fbd_vectors=fbd_vectors,
            numerical_results={"v1": v1, "v2": v2},
            simulation_timeline=[],
            concepts_used=[
                "momentum_conservation",
                "elastic_collision_1d",
                "coefficient_of_restitution",
            ],
        )

    def _solve_two_body_pulley(self, problem: ProblemSpec) -> DPASolution:
        """Solve Atwood Machine two-body pulley system."""
        m1 = problem.parameters.get("m1", 3.0)
        m2 = problem.parameters.get("m2", 2.0)
        g = problem.parameters.get("g", 9.81)

        # a = (m1 - m2)g / (m1 + m2)
        a = abs(m1 - m2) * g / (m1 + m2)
        # T = 2*m1*m2*g / (m1 + m2)
        T = (2.0 * m1 * m2 * g) / (m1 + m2)

        steps = [
            DPASolutionStep(
                step_number=1,
                title="Equations of Motion for Individual Masses",
                latex_formula=r"m_1 g - T = m_1 a, \quad T - m_2 g = m_2 a",
                description="Apply Newton's Second Law to both hanging masses with common string tension T.",
                values={"m1": m1, "m2": m2, "g": g},
            ),
            DPASolutionStep(
                step_number=2,
                title="Solve for Common System Acceleration",
                latex_formula=rf"a = \frac{{(m_1 - m_2)g}}{{m_1 + m_2}} = \frac{{({m1} - {m2})({g})}}{{{m1} + {m2}}} = \mathbf{{{a:.3f}\,\text{{m/s}}^2}}",
                description="Divide net driving gravitational force by total system inertia.",
                values={"acceleration": round(a, 3)},
            ),
            DPASolutionStep(
                step_number=3,
                title="Solve for String Tension",
                latex_formula=rf"T = \frac{{2m_1 m_2 g}}{{m_1 + m_2}} = \frac{{2({m1})({m2})({g})}}{{{m1 + m2}}} = \mathbf{{{T:.2f}\,\text{{N}}}}",
                description="Tension developed throughout the light inextensible string.",
                values={"tension": round(T, 3)},
            ),
        ]

        fbd_vectors = [
            FBDVectorSpec("Tension 1", r"\vec{T}", T, (0.0, 0.0), (0.0, 1.0), "#38bdf8"),
            FBDVectorSpec("Gravity 1", r"m_1\vec{g}", m1 * g, (0.0, 0.0), (0.0, -1.0), "#ef4444"),
        ]

        return DPASolution(
            problem_id=problem.problem_id,
            system_type="two_body_pulley",
            target_unknown=problem.target_unknown,
            answer_value=round(a, 3),
            answer_unit="m/s²",
            answer_latex=rf"a = {a:.3f}\,\text{{m/s}}^2, \quad T = {T:.2f}\,\text{{N}}",
            steps=steps,
            fbd_vectors=fbd_vectors,
            numerical_results={"acceleration": a, "tension": T},
            simulation_timeline=[],
            concepts_used=["newton_second_law", "pulley_systems", "tension", "two_body_dynamics"],
        )
