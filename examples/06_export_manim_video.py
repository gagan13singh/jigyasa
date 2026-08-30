"""
Example 06: Export Simulation to Manim Script
============================================

Demonstrates how PhysEngine computes the physics and exports
a ready-to-render Python Manim script for Scientia and Vidyastra.
"""

from physengine.core.simulation import Simulation
from physengine.core.world import World
from physengine.kinematics.projectile import ProjectileMotion
from physengine.mechanics.forces import UniformGravity
from physengine.mechanics.particle import Particle
from physengine.rendering.manim_renderer import export_to_manim_script


def main():
    print("Running Projectile Simulation in PhysEngine...")
    world = World(gravity=9.81)
    v0 = 35.0
    angle_deg = 50.0
    proj = ProjectileMotion(v0=v0, angle=angle_deg, g=9.81)

    ball = Particle(
        mass=1.0,
        position=(0, 0),
        velocity=proj.velocity_at(0.0),
        name="cannonball",
    )
    world.add(ball)
    world.add_force(UniformGravity())

    world.config.duration = proj.time_of_flight + 0.2
    world.config.timestep = 0.01

    sim = Simulation(world)
    history = sim.run()

    output_path = export_to_manim_script(
        history=history,
        scene_name="ProjectileManimDemo",
        title="2D Projectile Motion (u = 35 m/s, θ = 50°)",
        output_filepath="projectile_scene.py",
    )

    print(f"[SUCCESS] Generated Manim Scene Script: {output_path.resolve()}")
    print("To render video in 1080p, run:")
    print(f"  manim -pqh {output_path.name} ProjectileManimDemo")


if __name__ == "__main__":
    main()
