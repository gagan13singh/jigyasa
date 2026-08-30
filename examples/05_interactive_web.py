#!/usr/bin/env python3
"""
Example 05: Export Interactive HTML Animation
==============================================

Run a projectile simulation with drag and export a standalone
interactive HTML viewer that opens directly in your web browser.

No web server required — the HTML file is completely self-contained!
"""

import math
import webbrowser
from pathlib import Path

from physengine import (
    Drag,
    Particle,
    RK4Integrator,
    Simulation,
    UniformGravity,
    World,
    export_html_animation,
)


def main():
    print("PhysEngine - Exporting Interactive HTML Animation")
    print("=" * 60)

    # 1. Create world and projectile
    world = World(gravity=9.81)
    v0, angle_deg = 30.0, 50.0
    angle_rad = math.radians(angle_deg)

    ball = Particle(
        mass=1.0,
        position=(0, 0),
        velocity=(v0 * math.cos(angle_rad), v0 * math.sin(angle_rad)),
        name="cannonball",
    )
    world.add(ball)
    world.add_force(UniformGravity())
    # Add air resistance
    world.add_force(Drag(drag_coefficient=0.47, cross_section_area=0.03))

    world.config.timestep = 0.005
    world.config.duration = 6.0

    # 2. Run simulation
    sim = Simulation(world, integrator=RK4Integrator())
    history = sim.run()

    # 3. Export standalone interactive HTML animation
    output_path = Path("simulation_animation.html").resolve()
    export_html_animation(history, output_path, title="Cannonball with Air Drag")

    print(f"\n[SUCCESS] Generated standalone animation: {output_path}")
    print("Opening in your browser...\n")

    webbrowser.open(output_path.as_uri())


if __name__ == "__main__":
    main()
