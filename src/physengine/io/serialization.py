"""
physengine.io.serialization
===========================

Save and load simulations to/from JSON.

The format is version-tagged for forward compatibility.
A saved simulation captures:
- Configuration
- Entity definitions (position, velocity, mass, etc.)
- Force definitions
- Integrator choice
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from physengine.core.config import SimulationConfig
from physengine.core.entity import RigidBodyComponent, Transform
from physengine.core.world import World
from physengine.mechanics.particle import Particle

FORMAT_VERSION = "1.0.0"


def save_world(world: World, path: str | Path) -> None:
    """Save a World to a JSON file.

    Args:
        world: The world to save.
        path: File path to write to.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    data: dict[str, Any] = {
        "version": FORMAT_VERSION,
        "config": world.config.to_dict(),
        "entities": [],
    }

    for entity in world.entities:
        entity_data: dict[str, Any] = {
            "name": entity.name,
            "tags": list(entity.tags),
        }

        if entity.has_component(Transform):
            t = entity.get_component(Transform)
            entity_data["position"] = [t.position.x, t.position.y]
            entity_data["rotation"] = t.rotation

        if entity.has_component(RigidBodyComponent):
            rb = entity.get_component(RigidBodyComponent)
            entity_data["mass"] = rb.mass
            entity_data["velocity"] = [rb.velocity.x, rb.velocity.y]
            entity_data["is_static"] = rb.is_static
            entity_data["restitution"] = rb.restitution
            entity_data["linear_damping"] = rb.linear_damping

        data["entities"].append(entity_data)

    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_world(path: str | Path) -> World:
    """Load a World from a JSON file.

    Args:
        path: File path to read from.

    Returns:
        A World populated with entities from the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the format version is incompatible.
    """
    path = Path(path)

    with open(path) as f:
        data = json.load(f)

    version = data.get("version", "0.0.0")
    if version.split(".")[0] != FORMAT_VERSION.split(".")[0]:
        raise ValueError(
            f"Incompatible format version: {version} "
            f"(expected {FORMAT_VERSION.split('.')[0]}.x.x)"
        )

    config = SimulationConfig.from_dict(data.get("config", {}))
    world = World(config=config)

    for entity_data in data.get("entities", []):
        particle = Particle(
            name=entity_data.get("name", ""),
            mass=entity_data.get("mass", 1.0),
            position=tuple(entity_data.get("position", [0, 0])),
            velocity=tuple(entity_data.get("velocity", [0, 0])),
            is_static=entity_data.get("is_static", False),
            restitution=entity_data.get("restitution", 1.0),
            linear_damping=entity_data.get("linear_damping", 0.0),
        )

        for tag in entity_data.get("tags", []):
            particle.add_tag(tag)

        world.add(particle)

    return world
