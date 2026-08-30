"""
physengine.scientia.client
==========================

Scientia Platform Integration Client.
Allows Scientia services (Courses, Practice, DPA) to communicate seamlessly
with PhysEngine either in-process (direct Python import) or over HTTP REST API.
"""

from __future__ import annotations

from typing import Any

from physengine.scientia.schema import DPASolution, ProblemSpec
from physengine.scientia.service import ScientiaPhysicsService


class ScientiaPhysicsClient:
    """
    Client for Scientia Platform to interact with PhysEngine (Jigyasa).
    Drop this client directly into Scientia's codebase.
    """

    def __init__(self, service: ScientiaPhysicsService | None = None) -> None:
        # Default to high-performance in-process engine
        self._service = service or ScientiaPhysicsService()

    # ── Course Integration ───────────────────────────────────────────────────

    def get_chapter_simulations(self, chapter: str) -> list[dict[str, Any]]:
        """Retrieve all simulations for a specific course chapter."""
        return self._service.get_simulations_for_chapter(chapter)

    def render_lesson_card(self, sim_id: str) -> dict[str, Any]:
        """Generate embeddable interactive simulation card for lesson notes."""
        return self._service.generate_lesson_embed_card(sim_id)

    # ── DPA Integration ──────────────────────────────────────────────────────

    def solve_dpa_problem(self, problem_data: dict[str, Any] | ProblemSpec) -> DPASolution:
        """
        Solve student DPA problem and generate coupled numerical simulation.
        Returns:
            DPASolution with LaTeX derivation steps, FBD vectors, and 60 FPS frames.
        """
        return self._service.solve_and_visualize(problem_data)

    def get_related_concept_simulations(self, problem_data: dict[str, Any] | ProblemSpec) -> list[dict[str, Any]]:
        """Find concept simulation suggestions for a student working on a DPA problem."""
        return self._service.get_concepts_for_dpa(problem_data)

    # ── Full Knowledge Graph ────────────────────────────────────────────────

    def get_knowledge_graph(self) -> dict[str, Any]:
        """Export full NCERT Class 11-12 physics knowledge graph."""
        return self._service.knowledge_graph.export_graph()
