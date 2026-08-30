"""
Example 08: Scientia DPA (Dynamic Problem Architecture) Solver
==============================================================

Demonstrates how Scientia DPA generates verified step-by-step mathematical
solutions, Free-Body Diagrams, and coupled 60 FPS simulations for student problems.
"""

from physengine import ProblemSpec, ScientiaPhysicsClient, SystemType


def main() -> None:
    client = ScientiaPhysicsClient()

    print("=" * 70)
    print("[SCIENTIA DPA]: SOLVING STUDENT QUESTION")
    print("=" * 70)

    # 1. Student problem received by DPA engine
    problem = ProblemSpec(
        problem_id="dpa-kinematics-101",
        raw_question=(
            "A heavy wooden crate of mass 5.0 kg is pushed on a horizontal factory floor "
            "with a constant force of 20.0 N. The coefficient of friction between crate and floor "
            "is mu = 0.20. Calculate the normal reaction, the friction force, and the resulting acceleration."
        ),
        system_type=SystemType.BLOCK_HORIZONTAL,
        parameters={"mass": 5.0, "applied_force": 20.0, "mu": 0.20, "g": 9.81},
        target_unknown="acceleration",
    )

    print(f"\n[Raw Question]:\n{problem.raw_question}")

    # 2. PhysEngine DPA Solver execution
    solution = client.solve_dpa_problem(problem)

    print("\n" + "=" * 70)
    print("[VERIFIED STEP-BY-STEP MATHEMATICAL DERIVATION] (LaTeX)")
    print("=" * 70)
    for step in solution.steps:
        print(f"\nStep {step.step_number}: {step.title}")
        print(f"  Formula: {step.latex_formula}")
        print(f"  Explanation: {step.description}")
        print(f"  Computed Values: {step.values}")

    print("\n" + "=" * 70)
    print("[FINAL NUMERICAL ANSWER]")
    print("=" * 70)
    print(f"Result: {solution.answer_latex} ({solution.answer_value} {solution.answer_unit})")

    print("\n" + "=" * 70)
    print("[FREE BODY DIAGRAM (FBD) SPECIFICATION]")
    print("=" * 70)
    for vector in solution.fbd_vectors:
        print(
            f"  * Vector '{vector.name}' ({vector.label_latex}): "
            f"{vector.magnitude_n:.2f} N in direction {vector.vector} [Color: {vector.color}]"
        )

    print("\n" + "=" * 70)
    print("[60 FPS SIMULATION TIMELINE SNAPSHOTS]")
    print("=" * 70)
    print(f"Generated {len(solution.simulation_timeline)} frames of continuous physics playback.")
    first_frame = solution.simulation_timeline[0]
    last_frame = solution.simulation_timeline[-1]
    print(f"  * Start (t = {first_frame['t']:.2f}s): x = {first_frame['entities']['block']['x']:.2f}m, v = {first_frame['entities']['block']['speed']:.2f}m/s")
    print(f"  * End   (t = {last_frame['t']:.2f}s): x = {last_frame['entities']['block']['x']:.2f}m, v = {last_frame['entities']['block']['speed']:.2f}m/s")

    # 3. Concept Recommendation
    print("\n" + "=" * 70)
    print("[SUGGESTED CONCEPT SIMULATIONS FOR THIS PROBLEM]")
    print("=" * 70)
    concepts = client.get_related_concept_simulations(problem)
    for c in concepts:
        print(f"  * Concept: {c['name']} ({c['key_formula']})")
        for sim in c["simulations"]:
            print(f"    -> Launch Lab: [ {sim['id']} ] - {sim['title']}")


if __name__ == "__main__":
    main()
