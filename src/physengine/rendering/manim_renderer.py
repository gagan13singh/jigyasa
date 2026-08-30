"""
physengine.rendering.manim_renderer
===================================

Manim export pipeline for generating high-production educational videos
for Scientia, Vidyastra, and YouTube lessons.

Key Principle:
    Physics calculations are computed 100% in PhysEngine.
    This module takes the simulation `StateHistory` and generates clean,
    standalone Manim Python script code with smooth camera motion,
    vector overlays, and synchronized LaTeX formula annotations.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from physengine.core.state import StateHistory


def export_to_manim_script(
    history: StateHistory,
    scene_name: str = "PhysicsSimulationScene",
    title: str = "2D Projectile Motion",
    output_filepath: str | Path = "manim_scene.py",
) -> Path:
    """Generate a ready-to-render Python script for Manim Community Edition.

    To render the video:
        manim -pql manim_scene.py PhysicsSimulationScene

    Args:
        history: Simulation StateHistory recording from PhysEngine.
        scene_name: Name of the generated Manim Scene class.
        title: Title banner displayed at the top of the video.
        output_filepath: Destination .py script file path.

    Returns:
        Path to the generated script file.
    """
    path = Path(output_filepath)

    # Sample key trajectory waypoints (around 100 points for smooth Manim animation)
    snapshots = history.snapshots
    step_size = max(1, len(snapshots) // 120)
    sampled = snapshots[::step_size]

    points_data = []
    for s in sampled:
        for name, es in s.entities.items():
            points_data.append({
                "t": round(s.time, 3),
                "name": name,
                "x": round(es.position.x, 3),
                "y": round(es.position.y, 3),
                "vx": round(es.velocity.x, 3),
                "vy": round(es.velocity.y, 3),
            })

    script_content = f'''"""
Auto-generated Manim Scene by PhysEngine
=========================================
Topic: {title}
Generated for: Scientia & Vidyastra Educational Pipelines

To Render:
    manim -pql {path.name} {scene_name}
    manim -pqh {path.name} {scene_name}   # For 1080p 60fps
    manim -pqk {path.name} {scene_name}   # For 4K 60fps
"""

from manim import *
import numpy as np

SIMULATION_DATA = {points_data}

class {scene_name}(Scene):
    def construct(self):
        # 1. Title Banner
        title_tex = Tex(r"\\textbf{{{title}}}", font_size=42, color=BLUE_B)
        title_tex.to_edge(UP)
        self.play(Write(title_tex), run_time=1.0)

        # 2. Coordinate Axes Grid
        axes = Axes(
            x_range=[0, 100, 20],
            y_range=[0, 60, 15],
            x_length=10,
            y_length=5,
            axis_config={{"color": GREY_B, "include_numbers": True}},
        ).shift(DOWN * 0.5)

        labels = axes.get_axis_labels(x_label="x \\text{{ (m)}}", y_label="y \\text{{ (m)}}")
        self.play(Create(axes), Write(labels), run_time=1.2)

        # 3. Trajectory Curve & Animated Ball
        primary_name = SIMULATION_DATA[0]["name"]
        entity_pts = [d for d in SIMULATION_DATA if d["name"] == primary_name]

        dot = Dot(color=YELLOW, radius=0.12)
        dot.move_to(axes.c2p(entity_pts[0]["x"], entity_pts[0]["y"]))

        trail = TracedPath(dot.get_center, stroke_color=TEAL_B, stroke_width=4)

        # 4. Telemetry Readout
        telemetry = DecimalNumber(
            0.0,
            num_decimal_places=2,
            unit="\\text{{ s}}",
            font_size=28,
            color=YELLOW_B,
        ).to_corner(UR)
        time_label = Text("Time: ", font_size=24, color=WHITE).next_to(telemetry, LEFT)

        self.add(trail, dot, time_label, telemetry)
        self.wait(0.5)

        # 5. Animate along physics trajectory
        for i in range(1, len(entity_pts)):
            pt = entity_pts[i]
            target_pos = axes.c2p(pt["x"], pt["y"])
            dt = entity_pts[i]["t"] - entity_pts[i-1]["t"]

            self.play(
                dot.animate.move_to(target_pos),
                telemetry.animate.set_value(pt["t"]),
                rate_func=linear,
                run_time=max(0.02, dt * 0.8),
            )

        self.wait(2.0)
'''

    path.write_text(script_content, encoding="utf-8")
    return path
