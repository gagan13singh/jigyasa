"""
Example 07: Scientia Course Integration & Embeddable Simulations
================================================================

Demonstrates how Scientia Courses / CMS dynamically embeds interactive
physics simulations and derivation cards into course lessons.
"""

from physengine import ScientiaPhysicsClient


def main() -> None:
    # 1. Initialize Scientia Physics Client
    client = ScientiaPhysicsClient()

    print("=" * 70)
    print("[SCIENTIA COURSE PLATFORM]: LAWS OF MOTION MODULE")
    print("=" * 70)

    # 2. Query all simulations relevant for "Laws of Motion" chapter
    chapter_sims = client.get_chapter_simulations("Laws of Motion")
    print(f"\nFound {len(chapter_sims)} simulations mapped to 'Laws of Motion':")
    for idx, sim in enumerate(chapter_sims, 1):
        print(f"  {idx}. [{sim['id']}] {sim['title']} (Class {sim['class_grade']})")
        print(f"     Key Formula: {sim['key_formula_latex']}")
        print(f"     Tags: {', '.join(sim['tags'])}")

    # 3. Generate Course Lesson Embed Widget for "Road Banking with Friction"
    print("\n" + "=" * 70)
    print("[EMBED CARD GENERATION]: LESSON 'Banking of Curved Roads'")
    print("=" * 70)
    embed_card = client.render_lesson_card("banking-with-friction")

    print("\n[Embed Widget Payload for Scientia Frontend]:")
    print(f"Title: {embed_card['title']}")
    print(f"Formula: {embed_card['key_formula_latex']}")
    print("\nGenerated HTML Component:\n")
    print(embed_card["html_component"])

    print("\n[Interactive Sliders exposed to Student]:")
    for param in embed_card["parameters"]:
        print(
            f"  * {param['label']}: [{param['min_value']} {param['unit']} to {param['max_value']} {param['unit']}] "
            f"(default: {param['default_value']} {param['unit']})"
        )


if __name__ == "__main__":
    main()
