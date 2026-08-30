"""
physengine.scientia.service
===========================

Unified Scientia Physics Service Gateway.
Provides the primary interface for Scientia (Courses, Practice, DPA) to
access simulation catalogs, run DPA problem solvers, and embed interactive labs.
"""

from __future__ import annotations

from typing import Any

from physengine.scientia.knowledge_graph import PhysicsKnowledgeGraph
from physengine.scientia.registry import SimulationRegistry
from physengine.scientia.schema import DPASolution, ProblemSpec
from physengine.scientia.solver import ProblemSolver


class ScientiaPhysicsService:
    """
    Primary service adapter consumed by Scientia platform.
    Decouples course CMS and DPA question banks from raw numerical physics math.
    """

    def __init__(self) -> None:
        self.registry = SimulationRegistry()
        self.solver = ProblemSolver()
        self.knowledge_graph = PhysicsKnowledgeGraph()

    # ── 1. Course & CMS Integration ─────────────────────────────────────────

    def get_catalog(self) -> list[dict[str, Any]]:
        """Return the complete simulation registry catalog as dictionaries."""
        return [s.to_dict() for s in self.registry.list_all()]

    def get_simulation_metadata(self, sim_id: str) -> dict[str, Any] | None:
        """Get structured metadata for a specific simulation."""
        sim = self.registry.get(sim_id)
        return sim.to_dict() if sim else None

    def get_simulations_for_chapter(self, chapter_name: str) -> list[dict[str, Any]]:
        """Find all simulations mapped to a specific curriculum chapter."""
        return [s.to_dict() for s in self.registry.find_by_chapter(chapter_name)]

    def generate_lesson_embed_card(self, sim_id: str) -> dict[str, Any]:
        """
        Generate embeddable widget metadata for Scientia Course Notes.
        E.g. Class 11 -> Physics -> Laws of Motion -> Notes
        """
        sim = self.registry.get(sim_id)
        if not sim:
            return {"error": f"Simulation '{sim_id}' not found"}

        html_snippet = rf"""<div class="scientia-sim-card" data-sim-id="{sim.id}">
  <div class="sim-card-badge">&#x1F9EA; Explore this concept</div>
  <div class="sim-card-title">{sim.title}</div>
  <div class="sim-card-formula">\({sim.key_formula_latex}\)</div>
  <p class="sim-card-desc">{sim.description}</p>
  <a href="/simulate?id={sim.id}" target="_blank" class="sim-card-btn">Open Simulation &rarr;</a>
</div>"""

        return {
            "simulation_id": sim.id,
            "title": sim.title,
            "chapter": sim.chapter,
            "key_formula_latex": sim.key_formula_latex,
            "html_component": html_snippet,
            "tags": sim.tags,
            "parameters": [p.__dict__ for p in sim.parameters],
        }

    # ── 2. DPA (Dynamic Problem Architecture) Integration ───────────────────

    def solve_and_visualize(self, problem: ProblemSpec | dict[str, Any]) -> DPASolution:
        """
        Core DPA API:
        Receives a structured physics problem and returns:
        1. Step-by-step LaTeX verified pedagogical derivation
        2. Free-Body Diagram force vector specs
        3. 60 FPS numerical simulation trajectory matching the exact solution!
        """
        spec = ProblemSpec.from_dict(problem) if isinstance(problem, dict) else problem
        return self.solver.solve(spec)

    # ── 3. Knowledge Graph & Recommendation ─────────────────────────────────

    def get_concepts_for_dpa(self, problem: ProblemSpec | dict[str, Any]) -> list[dict[str, Any]]:
        """Identify relevant concepts and simulation links for a DPA problem."""
        if isinstance(problem, dict):
            sys_type = problem.get("system_type", "block_horizontal")
        else:
            sys_type = problem.system_type.value

        concept_nodes = self.knowledge_graph.get_dpa_concepts(sys_type)
        results = []
        for c in concept_nodes:
            sims = [self.registry.get(sid) for sid in c.simulation_ids if self.registry.get(sid)]
            results.append(
                {
                    "concept_id": c.id,
                    "name": c.name,
                    "key_formula": c.key_formula,
                    "description": c.description,
                    "simulations": [s.to_dict() for s in sims if s is not None],
                }
            )
        return results

    def export_api_manifest(self) -> dict[str, Any]:
        """Export comprehensive API manifest for Scientia backend integration."""
        return {
            "version": "1.0.0",
            "service_name": "Scientia Physics Service (Jigyasa)",
            "total_simulations": len(self.registry.list_all()),
            "catalog": self.get_catalog(),
            "knowledge_graph": self.knowledge_graph.export_graph(),
            "supported_dpa_systems": [
                "block_horizontal",
                "block_incline",
                "projectile",
                "circular_banking",
                "spring_mass",
                "collision_1d",
                "two_body_pulley",
            ],
        }
