"""
physengine.io.export
====================

Export simulation data in various formats (CSV, JSON).

This module handles exporting trajectory and history data for
external consumption — data analysis tools, spreadsheets, or
web visualization frontends.
"""

from __future__ import annotations

import json
from pathlib import Path

from physengine.analysis.recorder import StateRecorder
from physengine.core.state import StateHistory


def export_history_csv(
    history: StateHistory,
    entity_name: str,
    path: str | Path,
) -> None:
    """Export an entity's trajectory from history to CSV.

    Args:
        history: Simulation state history.
        entity_name: Name of the entity to export.
        path: Output file path.
    """
    recorder = StateRecorder(history)
    trajectory = recorder.get_trajectory(entity_name)
    trajectory.to_csv(path)


def export_history_json(
    history: StateHistory,
    entity_name: str,
    path: str | Path,
) -> None:
    """Export an entity's trajectory from history to JSON.

    Args:
        history: Simulation state history.
        entity_name: Name of the entity to export.
        path: Output file path.
    """
    recorder = StateRecorder(history)
    trajectory = recorder.get_trajectory(entity_name)
    trajectory.to_json(path)


def export_all_entities_csv(
    history: StateHistory,
    output_dir: str | Path,
) -> list[Path]:
    """Export trajectories for all entities, one CSV per entity.

    Args:
        history: Simulation state history.
        output_dir: Directory to write CSV files to.

    Returns:
        List of created file paths.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    recorder = StateRecorder(history)
    paths: list[Path] = []

    for name in recorder.entity_names:
        file_path = output_dir / f"{name}_trajectory.csv"
        trajectory = recorder.get_trajectory(name)
        trajectory.to_csv(file_path)
        paths.append(file_path)

    return paths


def export_summary_json(
    history: StateHistory,
    path: str | Path,
) -> None:
    """Export a summary of the entire simulation to JSON.

    Includes metadata, entity list, and key metrics.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    recorder = StateRecorder(history)

    summary = {
        "duration": recorder.duration,
        "num_snapshots": len(history),
        "entities": recorder.entity_names,
        "total_kinetic_energies": {
            "initial": (
                recorder.total_kinetic_energies[0]
                if recorder.total_kinetic_energies
                else 0
            ),
            "final": (
                recorder.total_kinetic_energies[-1]
                if recorder.total_kinetic_energies
                else 0
            ),
        },
    }

    with open(path, "w") as f:
        json.dump(summary, f, indent=2)


def export_html_animation(
    history: StateHistory,
    path: str | Path,
    title: str = "PhysEngine Simulation",
) -> None:
    """Export a simulation history to a standalone, offline interactive HTML viewer.

    Args:
        history: Simulation state history.
        path: File path to write the HTML file to.
        title: Title for the simulation viewer.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

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

    sim_payload = json.dumps({"title": title, "snapshots": snapshots})

    template_file = Path(__file__).parents[1] / "visualizer" / "template.html"
    if template_file.exists():
        template = template_file.read_text(encoding="utf-8")
        # Embed payload directly
        injection = f"<script>window.__EMBEDDED_SIM_DATA__ = {sim_payload};</script>"
        html_content = template.replace("<head>", f"<head>\n  {injection}")
    else:
        html_content = f"<html><body><h1>{title}</h1></body></html>"

    with open(path, "w", encoding="utf-8") as f:
        f.write(html_content)
