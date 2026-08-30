"""
physengine.visualizer.server
============================

Local web server for the interactive visualizer.

Launches a lightweight local server and opens the interactive
Class 9-12 physics simulation playground in the user's default browser.
"""

from __future__ import annotations

import http.server
import json
import math
import socketserver
import threading
import urllib.parse
import webbrowser
from pathlib import Path
from typing import Any

from physengine.core.simulation import Simulation
from physengine.core.world import World
from physengine.electromagnetism.coulomb import (
    CoulombForce,
    ElectricChargeComponent,
    UniformElectricField,
)
from physengine.electromagnetism.lorentz import UniformLorentzForce
from physengine.kinematics.projectile import ProjectileMotion
from physengine.math.vector import Vector2
from physengine.mechanics.fluids import BuoyantForce, StokesDrag
from physengine.mechanics.forces import (
    ConstantForce,
    Drag,
    PointGravity,
    Spring,
    UniformGravity,
)
from physengine.mechanics.particle import Particle
from physengine.mechanics.rotational import (
    InertiaShape,
    RollingBodyOnIncline,
)
from physengine.solvers.euler import EulerIntegrator, SemiImplicitEulerIntegrator
from physengine.solvers.rk4 import RK4Integrator
from physengine.solvers.verlet import VelocityVerletIntegrator

SOLVERS = {
    "rk4": RK4Integrator,
    "verlet": VelocityVerletIntegrator,
    "semi_implicit_euler": SemiImplicitEulerIntegrator,
    "euler": EulerIntegrator,
}


def run_preset_simulation(preset_id: str, params: dict[str, Any]) -> dict[str, Any]:
    """Run a physics simulation for a given preset with user parameters."""
    solver_key = params.get("solver", "rk4").lower()
    integrator_cls = SOLVERS.get(solver_key, RK4Integrator)
    dt = float(params.get("dt", 0.005))
    g_val = float(params.get("gravity", 9.81))

    world = World(gravity=g_val)
    world.config.timestep = dt
    world.config.record_interval = 1

    integrator = integrator_cls()

    # ── Unit 1: Kinematics ─────────────────────────────────────────────
    if preset_id == "projectile":
        v0 = float(params.get("v0", 30.0))
        angle_deg = float(params.get("angle", 45.0))
        angle_rad = math.radians(angle_deg)
        drag_on = bool(params.get("drag", False))

        ball = Particle(
            mass=float(params.get("mass", 1.0)),
            position=(0, 0),
            velocity=(v0 * math.cos(angle_rad), v0 * math.sin(angle_rad)),
            name="projectile",
        )
        world.add(ball)
        world.add_force(UniformGravity())

        if drag_on:
            cd = float(params.get("drag_cd", 0.47))
            area = float(params.get("drag_area", 0.02))
            world.add_force(Drag(drag_coefficient=cd, cross_section_area=area))

        proj = ProjectileMotion(v0=v0, angle=angle_deg, g=g_val)
        duration = min(proj.time_of_flight * 1.1 if proj.time_of_flight > 0 else 5.0, 20.0)
        world.config.duration = max(duration, 2.0)

    elif preset_id == "cliff_projectile":
        v0 = float(params.get("v0", 25.0))
        angle_deg = float(params.get("angle", 0.0))
        h = float(params.get("height", 45.0))
        angle_rad = math.radians(angle_deg)

        ball = Particle(
            mass=float(params.get("mass", 1.0)),
            position=(0, h),
            velocity=(v0 * math.cos(angle_rad), v0 * math.sin(angle_rad)),
            name="projectile",
        )
        world.add(ball)
        world.add_force(UniformGravity())

        proj = ProjectileMotion(v0=v0, angle=angle_deg, g=g_val, height=h)
        world.config.duration = proj.time_of_flight + 0.5

    elif preset_id == "freefall":
        h = float(params.get("height", 80.0))
        u = float(params.get("v0", 0.0))
        ball = Particle(
            mass=float(params.get("mass", 1.0)),
            position=(0, h),
            velocity=(0, u),
            name="ball",
        )
        world.add(ball)
        world.add_force(UniformGravity())
        disc = u * u + 2 * g_val * h
        t_fall = (u + math.sqrt(disc)) / g_val if g_val > 0 and disc >= 0 else 5.0
        world.config.duration = t_fall + 0.5

    elif preset_id == "car_braking":
        # 1D Uniformly Accelerated / Braking Motion
        v0 = float(params.get("v0", 25.0)) # 90 km/h = 25 m/s
        mu = float(params.get("friction_mu", 0.7))
        a_brake = mu * g_val

        car = Particle(
            mass=1200.0,
            position=(0, 0),
            velocity=(v0, 0),
            name="car",
        )
        world.add(car)
        # Constant braking force opposing motion
        world.add_force_to(car, ConstantForce(Vector2(-a_brake * 1200.0, 0)))
        t_stop = v0 / a_brake if a_brake > 0 else 5.0
        world.config.duration = t_stop + 0.5

    elif preset_id == "river_swimmer":
        # Relative Motion: Boat crossing a river with water current
        v_river = float(params.get("v_river", 4.0))
        v_boat = float(params.get("v0", 6.0))
        theta_deg = float(params.get("angle", 90.0)) # 90° = directly across
        theta_rad = math.radians(theta_deg)

        # Net velocity = v_boat_relative + v_river
        vx_net = v_boat * math.cos(theta_rad) + v_river
        vy_net = v_boat * math.sin(theta_rad)

        boat = Particle(
            mass=200.0,
            position=(0, 0),
            velocity=(vx_net, vy_net),
            name="boat",
        )
        world.add(boat)
        world.config.duration = 60.0 / max(vy_net, 0.5)

    # ── Unit 2: Laws of Motion & Friction ───────────────────────────────
    elif preset_id == "incline":
        theta_deg = float(params.get("incline_angle", 30.0))
        mu_k = float(params.get("friction_mu", 0.15))
        m = float(params.get("mass", 2.0))
        theta_rad = math.radians(theta_deg)

        a_ramp = max(0.0, g_val * (math.sin(theta_rad) - mu_k * math.cos(theta_rad)))
        fx = a_ramp * m * math.cos(theta_rad)
        fy = -a_ramp * m * math.sin(theta_rad)

        ramp_length = 50.0
        start_x = 0.0
        start_y = ramp_length * math.sin(theta_rad)

        block = Particle(
            mass=m,
            position=(start_x, start_y),
            velocity=(0, 0),
            name="block",
        )
        world.add(block)
        world.add_force_to(block, ConstantForce(Vector2(fx, fy)))
        t_slide = math.sqrt(2 * ramp_length / a_ramp) if a_ramp > 0.01 else 5.0
        world.config.duration = t_slide + 0.5

    elif preset_id == "atwood":
        # Atwood machine connected bodies
        m1 = float(params.get("mass", 3.0))
        m2 = float(params.get("mass2", 2.0))
        a_net = abs(m1 - m2) / (m1 + m2) * g_val

        b1 = Particle(
            mass=m1, position=(-4, 0), velocity=(0, -0.01 if m1 > m2 else 0.01), name="mass_1"
        )
        b2 = Particle(
            mass=m2, position=(4, 0), velocity=(0, 0.01 if m1 > m2 else -0.01), name="mass_2"
        )
        world.add(b1)
        world.add(b2)
        world.add_force_to(b1, ConstantForce(Vector2(0, -a_net * m1 if m1 > m2 else a_net * m1)))
        world.add_force_to(b2, ConstantForce(Vector2(0, a_net * m2 if m1 > m2 else -a_net * m2)))
        world.config.duration = 6.0

    elif preset_id == "collision":
        world = World(gravity=0)
        m1 = float(params.get("mass", 2.0))
        m2 = float(params.get("mass2", 1.0))
        v1 = float(params.get("v0", 15.0))
        v2 = float(params.get("v2", -5.0))

        b1 = Particle(mass=m1, position=(-25, 0), velocity=(v1, 0), name="ball_1")
        b2 = Particle(mass=m2, position=(25, 0), velocity=(v2, 0), name="ball_2")
        world.add(b1)
        world.add(b2)
        world.config.duration = 5.0

    # ── Unit 3: Rotational Dynamics & Inertia Race ─────────────────────
    elif preset_id == "rolling_race":
        # Classic Class 11 Race down an incline: Solid Sphere vs Solid Cylinder vs Ring
        theta_deg = float(params.get("incline_angle", 30.0))
        theta_rad = math.radians(theta_deg)
        m = 1.0
        r = 1.0
        ramp_len = 50.0

        sphere_calc = RollingBodyOnIncline(
            InertiaShape.SOLID_SPHERE, m, r, theta_deg, ramp_len, g=g_val
        )
        cyl_calc = RollingBodyOnIncline(
            InertiaShape.SOLID_CYLINDER, m, r, theta_deg, ramp_len, g=g_val
        )
        ring_calc = RollingBodyOnIncline(
            InertiaShape.HOOP_OR_RING, m, r, theta_deg, ramp_len, g=g_val
        )

        # 3 lanes on the ramp
        start_y = ramp_len * math.sin(theta_rad)

        p_sphere = Particle(mass=m, position=(0, start_y + 4), velocity=(0, 0), name="sphere")
        p_cyl = Particle(mass=m, position=(0, start_y), velocity=(0, 0), name="cylinder")
        p_ring = Particle(mass=m, position=(0, start_y - 4), velocity=(0, 0), name="ring")

        world.add(p_sphere)
        world.add(p_cyl)
        world.add(p_ring)

        # Apply rolling accelerations along incline
        a_s = sphere_calc.acceleration
        a_c = cyl_calc.acceleration
        a_r = ring_calc.acceleration

        f_sphere = Vector2(a_s * math.cos(theta_rad), -a_s * math.sin(theta_rad)) * m
        f_cyl = Vector2(a_c * math.cos(theta_rad), -a_c * math.sin(theta_rad)) * m
        f_ring = Vector2(a_r * math.cos(theta_rad), -a_r * math.sin(theta_rad)) * m

        world.add_force_to(p_sphere, ConstantForce(f_sphere))
        world.add_force_to(p_cyl, ConstantForce(f_cyl))
        world.add_force_to(p_ring, ConstantForce(f_ring))

        world.config.duration = max(ring_calc.time_to_bottom + 1.0, 5.0)

    # ── Unit 4: Work, Energy & SHM ─────────────────────────────────────
    elif preset_id == "pendulum":
        L = float(params.get("length", 4.0))
        theta0_deg = float(params.get("angle", 30.0))
        theta0_rad = math.radians(theta0_deg)
        m = float(params.get("mass", 1.0))

        x0 = L * math.sin(theta0_rad)
        y0 = -L * math.cos(theta0_rad)

        bob = Particle(mass=m, position=(x0, y0), velocity=(0, 0), name="bob")
        world.add(bob)
        spring = Spring(stiffness=2500.0, anchor=Vector2.zero(), rest_length=L, damping=0.01)
        world.add_force_to(bob, spring)
        world.add_force(UniformGravity())
        world.config.duration = 15.0

    elif preset_id == "spring":
        k = float(params.get("stiffness", 15.0))
        damping = float(params.get("damping", 0.02))
        x0 = float(params.get("amplitude", 8.0))
        m_val = float(params.get("mass", 1.0))

        ball = Particle(mass=m_val, position=(x0, 0), velocity=(0, 0), name="mass")
        world.add(ball)
        spring = Spring(stiffness=k, anchor=Vector2.zero(), rest_length=0.0, damping=damping)
        world.add_force_to(ball, spring)
        world.config.duration = 15.0

    elif preset_id == "vertical_circle":
        # Motion in a Vertical Circle: Loop-the-Loop with radius R
        R = float(params.get("radius", 5.0))
        u_factor = float(params.get("v0_factor", 1.05)) # factor of critical velocity sqrt(5gR)
        v_crit = math.sqrt(5.0 * g_val * R)
        u = u_factor * v_crit

        cart = Particle(mass=1.0, position=(0, -R), velocity=(u, 0), name="cart")
        world.add(cart)
        # Stiff constraint towards center (0, 0)
        track = Spring(stiffness=4000.0, anchor=Vector2.zero(), rest_length=R, damping=0.01)
        world.add_force_to(cart, track)
        world.add_force(UniformGravity())
        world.config.duration = 10.0

    # ── Unit 5: Fluids & Viscosity ─────────────────────────────────────
    elif preset_id == "stokes":
        m = float(params.get("mass", 1.0))
        r = float(params.get("radius", 0.05))
        eta = float(params.get("viscosity", 1.2))

        ball = Particle(mass=m, position=(0, 60), velocity=(0, 0), name="droplet")
        world.add(ball)
        world.add_force(UniformGravity())
        world.add_force(StokesDrag(radius=r, dynamic_viscosity=eta))
        world.config.duration = 8.0

    elif preset_id == "buoyancy":
        m = float(params.get("mass", 2.0))
        v_sub = float(params.get("volume", 0.003)) # 3 liters

        block = Particle(mass=m, position=(0, 20), velocity=(0, 0), name="block")
        world.add(block)
        world.add_force(UniformGravity())
        world.add_force(
            BuoyantForce(fluid_density=1000.0, submerged_volume=v_sub, fluid_surface_y=0.0)
        )
        world.add_force(StokesDrag(radius=0.1, dynamic_viscosity=0.8))
        world.config.duration = 10.0

    # ── Unit 6: Gravitation ────────────────────────────────────────────
    elif preset_id == "orbit":
        world = World(gravity=0)
        m_sun = 1200.0
        m_planet = 1.0
        r = 12.0
        G = 10.0
        # Slightly elliptical orbit (v = 0.9 * v_circular)
        v_circ = math.sqrt(G * m_sun / r)
        v_orbit = v_circ * float(params.get("eccentricity_factor", 0.92))

        sun = Particle(mass=m_sun, position=(0, 0), is_static=True, name="sun")
        planet = Particle(mass=m_planet, position=(r, 0), velocity=(0, v_orbit), name="planet")
        world.add(sun)
        world.add_force_to(
            planet,
            PointGravity(
                source_mass=m_sun, source_position=Vector2.zero(), G=G, softening=0.5
            ),
        )
        world.add(planet)
        world.config.duration = 25.0

    # ── Unit 7: Class 12 Electromagnetism & Modern Physics ───────────────
    elif preset_id == "cyclotron":
        world = World(gravity=0)
        q = float(params.get("charge", 1.0))
        m = float(params.get("mass", 1.0))
        v_init = float(params.get("v0", 25.0))
        Bz = float(params.get("b_field", 1.5))

        electron = Particle(mass=m, position=(0, 0), velocity=(v_init, 0), name="charge")
        electron.add_component(ElectricChargeComponent(charge=q))
        world.add(electron)
        world.add_force(UniformLorentzForce(magnetic_field_z=Bz))
        world.config.duration = 10.0

    elif preset_id == "electron_deflection":
        # Parallel plate capacitor deflection
        world = World(gravity=0)
        q = -1.0 # electron negative charge
        m = 1.0
        vx0 = float(params.get("v0", 30.0))
        Ey = float(params.get("e_field", 50.0)) # Electric field downwards

        electron = Particle(mass=m, position=(-30, 0), velocity=(vx0, 0), name="electron")
        electron.add_component(ElectricChargeComponent(charge=q))
        world.add(electron)
        world.add_force(UniformElectricField(Vector2(0, -Ey)))
        world.config.duration = 3.0

    elif preset_id == "rutherford":
        # Alpha particle scattering off heavy Gold Nucleus (Coulomb repulsion)
        world = World(gravity=0)
        m_gold = 10000.0
        q_gold = 79.0 # Au nucleus Z=79
        q_alpha = 2.0 # He nucleus Z=2
        m_alpha = 4.0
        v_alpha = float(params.get("v0", 40.0))
        b_impact = float(params.get("impact_param", 3.0)) # Impact parameter b

        gold = Particle(mass=m_gold, position=(0, 0), is_static=True, name="gold_nucleus")
        alpha = Particle(
            mass=m_alpha,
            position=(-40, b_impact),
            velocity=(v_alpha, 0),
            name="alpha_particle",
        )
        alpha.add_component(ElectricChargeComponent(charge=q_alpha))

        world.add(gold)
        world.add(alpha)
        world.add_force_to(
            alpha,
            CoulombForce(
                source_charge=q_gold,
                source_position=Vector2.zero(),
                k_e=20.0,
                softening=0.8,
            ),
        )
        world.config.duration = 3.0

    else:
        ball = Particle(mass=1.0, position=(0, 50), name="ball")
        world.add(ball)
        world.add_force(UniformGravity())
        world.config.duration = 4.0

    sim = Simulation(world, integrator=integrator)
    history = sim.run()

    # Pack snapshot data
    snapshots = []
    for s in history.snapshots:
        entities_data = {}
        for name, es in s.entities.items():
            entities_data[name] = {
                "name": es.name,
                "x": round(es.position.x, 5),
                "y": round(es.position.y, 5),
                "vx": round(es.velocity.x, 5),
                "vy": round(es.velocity.y, 5),
                "ax": round(es.acceleration.x, 5),
                "ay": round(es.acceleration.y, 5),
                "speed": round(es.velocity.magnitude, 5),
                "ke": round(es.kinetic_energy, 5),
            }
        snapshots.append({
            "t": round(s.time, 4),
            "step": s.step,
            "entities": entities_data,
        })

    return {
        "preset": preset_id,
        "solver": integrator.name,
        "order": integrator.order,
        "dt": dt,
        "duration": world.config.duration,
        "snapshots": snapshots,
    }


def get_html_content() -> str:
    """Read the visualizer HTML template."""
    template_path = Path(__file__).parent / "template.html"
    if template_path.exists():
        return template_path.read_text(encoding="utf-8")
    return "<h1>Template not found</h1>"


class VisualizerRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler serving the visualizer GUI and simulation API."""

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            html = get_html_content()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html.encode("utf-8"))))
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_error(404, "Not Found")

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/simulate":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            params = json.loads(body.decode("utf-8")) if body else {}
            preset_id = params.get("preset", "projectile")

            result = run_preset_simulation(preset_id, params)
            data = json.dumps(result).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_error(404, "Not Found")

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress standard HTTP server request logs for clean terminal output."""
        return


def start_visualizer(port: int = 8000, open_browser: bool = True) -> None:
    """Start the interactive visualizer server and open in browser."""
    while True:
        try:
            server = socketserver.TCPServer(("127.0.0.1", port), VisualizerRequestHandler)
            break
        except OSError:
            port += 1

    url = f"http://127.0.0.1:{port}"
    print("\n========================================================")
    print(f"  PhysEngine Visualizer Running at: {url}")
    print("  Press Ctrl+C in terminal to stop.")
    print("========================================================\n")

    if open_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Visualizer...")
        server.shutdown()
