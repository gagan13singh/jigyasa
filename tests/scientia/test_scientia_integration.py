"""
tests.scientia.test_scientia_integration
========================================

Automated test suite verifying the Scientia Learning platform integration:
1. Simulation Registry catalog lookups and filtering
2. Structured ProblemSpec parsing & DPA ProblemSolver accuracy
3. Free Body Diagram vector generation & simulation timeline matching
4. Physics Knowledge Graph relational queries
5. Unified ScientiaPhysicsService gateway operations
"""

import pytest

from physengine import (
    DPASolution,
    PhysicsKnowledgeGraph,
    ProblemSolver,
    ProblemSpec,
    ScientiaPhysicsService,
    SimulationRegistry,
    SystemType,
)


class TestSimulationRegistry:
    """Tests for the curriculum simulation registry."""

    def test_registry_initialization(self) -> None:
        registry = SimulationRegistry()
        sims = registry.list_all()
        assert len(sims) >= 12
        assert registry.get("newton-second-law") is not None
        assert registry.get("banking-with-friction") is not None
        assert registry.get("projectile-motion") is not None

    def test_find_by_chapter(self) -> None:
        registry = SimulationRegistry()
        lom_sims = registry.find_by_chapter("Laws of Motion")
        assert len(lom_sims) >= 6
        ids = [s.id for s in lom_sims]
        assert "newton-second-law" in ids
        assert "static-friction" in ids

    def test_find_by_tag(self) -> None:
        registry = SimulationRegistry()
        friction_sims = registry.find_by_tag("friction")
        assert len(friction_sims) >= 4
        for s in friction_sims:
            assert "friction" in [t.lower() for t in s.tags]

    def test_search(self) -> None:
        registry = SimulationRegistry()
        results = registry.search("parabolic")
        assert len(results) >= 1
        assert results[0].id == "projectile-motion"


class TestProblemSolver:
    """Tests for the DPA ProblemSolver and verified calculations."""

    def test_horizontal_block_dpa_solver(self) -> None:
        """
        Verify the exact problem from user specification:
        Mass = 5 kg, Applied Force = 20 N, mu = 0.2, g = 9.81
        N = 5 * 9.81 = 49.05 N
        f = 0.2 * 49.05 = 9.81 N
        F_net = 20 - 9.81 = 10.19 N
        a = 10.19 / 5 = 2.038 m/s^2
        """
        problem = ProblemSpec(
            problem_id="dpa-001",
            raw_question="A block of mass 5 kg is placed on a rough horizontal surface with mu=0.2. Force 20 N is applied. Find acceleration.",
            system_type=SystemType.BLOCK_HORIZONTAL,
            parameters={"mass": 5.0, "applied_force": 20.0, "mu": 0.2, "g": 9.81},
            target_unknown="acceleration",
        )

        solver = ProblemSolver()
        solution = solver.solve(problem)

        assert isinstance(solution, DPASolution)
        assert pytest.approx(solution.answer_value, abs=1e-3) == 2.038
        assert solution.answer_unit == "m/s²"
        assert len(solution.steps) >= 5
        assert len(solution.fbd_vectors) == 4
        assert len(solution.simulation_timeline) > 0

        # Verify that simulation timeline matches analytical acceleration
        first_frame = solution.simulation_timeline[0]
        assert "block" in first_frame["entities"]
        assert pytest.approx(first_frame["entities"]["block"]["ax"], abs=1e-3) == 2.038

    def test_incline_block_dpa_solver(self) -> None:
        """
        Incline 30 deg, m = 2.0 kg, mu = 0.2, g = 9.81
        a = 9.81 * (sin(30 deg) - 0.2 * cos(30 deg)) = 9.81 * (0.5 - 0.1732) = 3.206 m/s^2
        """
        problem = ProblemSpec(
            problem_id="dpa-002",
            raw_question="A 2 kg block slides down a 30 degree incline with mu=0.2. Find its acceleration.",
            system_type=SystemType.BLOCK_INCLINE,
            parameters={"mass": 2.0, "incline_deg": 30.0, "mu": 0.2, "g": 9.81},
            target_unknown="acceleration",
        )

        solver = ProblemSolver()
        solution = solver.solve(problem)

        assert pytest.approx(solution.answer_value, abs=1e-3) == 3.206
        assert len(solution.steps) >= 4
        assert "inclined_plane" in solution.concepts_used

    def test_projectile_dpa_solver(self) -> None:
        """
        Projectile: u = 20 m/s, theta = 45 deg, g = 9.81
        R = 20^2 * sin(90 deg) / 9.81 = 40.77 m
        """
        problem = ProblemSpec(
            problem_id="dpa-003",
            raw_question="A ball is projected at 20 m/s at 45 degrees. Find horizontal range.",
            system_type=SystemType.PROJECTILE,
            parameters={"velocity": 20.0, "angle": 45.0, "g": 9.81, "mass": 1.0},
            target_unknown="range",
        )

        solver = ProblemSolver()
        solution = solver.solve(problem)

        assert pytest.approx(solution.answer_value, abs=1e-2) == 40.77
        assert solution.answer_unit == "m"

    def test_two_body_pulley_solver(self) -> None:
        """
        Atwood machine: m1 = 3 kg, m2 = 2 kg, g = 9.81
        a = (3 - 2)*9.81 / 5 = 1.962 m/s^2
        T = 2*3*2*9.81 / 5 = 23.544 N
        """
        problem = ProblemSpec(
            problem_id="dpa-004",
            raw_question="Two masses 3kg and 2kg are connected across a frictionless pulley. Find acceleration.",
            system_type=SystemType.TWO_BODY_PULLEY,
            parameters={"m1": 3.0, "m2": 2.0, "g": 9.81},
            target_unknown="acceleration",
        )

        solver = ProblemSolver()
        solution = solver.solve(problem)

        assert pytest.approx(solution.answer_value, abs=1e-3) == 1.962
        assert pytest.approx(solution.numerical_results["tension"], abs=1e-2) == 23.54


class TestPhysicsKnowledgeGraph:
    """Tests for the relational Physics Knowledge Graph."""

    def test_knowledge_graph_queries(self) -> None:
        kg = PhysicsKnowledgeGraph()
        node = kg.get_concept("newton_second_law")
        assert node is not None
        assert "newton-second-law" in node.simulation_ids
        assert "block_horizontal" in node.dpa_system_types

    def test_chapter_concepts(self) -> None:
        kg = PhysicsKnowledgeGraph()
        lom_concepts = kg.get_concepts_for_chapter("Laws of Motion")
        assert len(lom_concepts) >= 5
        concept_ids = [c.id for c in lom_concepts]
        assert "static_friction" in concept_ids
        assert "banking_of_roads" in concept_ids


class TestScientiaPhysicsService:
    """Tests for the primary service gateway consumed by Scientia."""

    def test_service_catalog_and_embed(self) -> None:
        service = ScientiaPhysicsService()
        catalog = service.get_catalog()
        assert len(catalog) >= 12

        card = service.generate_lesson_embed_card("newton-second-law")
        assert card["simulation_id"] == "newton-second-law"
        assert "scientia-sim-card" in card["html_component"]
        assert "Open Simulation" in card["html_component"]

    def test_service_dpa_end_to_end(self) -> None:
        service = ScientiaPhysicsService()
        problem_dict = {
            "problem_id": "dpa-test-101",
            "raw_question": "5kg block, F=20N, mu=0.2 on horizontal floor",
            "system_type": "block_horizontal",
            "parameters": {"mass": 5.0, "applied_force": 20.0, "mu": 0.2, "g": 9.81},
            "target_unknown": "acceleration",
        }

        solution = service.solve_and_visualize(problem_dict)
        assert solution.answer_value == pytest.approx(2.038, abs=1e-3)
        assert len(solution.steps) >= 5
        assert len(solution.simulation_timeline) > 0

        concepts = service.get_concepts_for_dpa(problem_dict)
        assert len(concepts) >= 1
        c_names = [c["name"] for c in concepts]
        assert any("Newton" in name for name in c_names)

    def test_service_manifest(self) -> None:
        service = ScientiaPhysicsService()
        manifest = service.export_api_manifest()
        assert manifest["service_name"] == "Scientia Physics Service (Jigyasa)"
        assert manifest["total_simulations"] >= 12
        assert "block_horizontal" in manifest["supported_dpa_systems"]
