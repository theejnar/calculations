"""CLI interface for the area calculator via triangulation."""

# pylint: disable=too-many-locals,too-many-statements

from area import calculate_area, MeasurementError


def main():
    """Run the interactive area calculator CLI."""
    print("=" * 60)
    print("  Area Calculator via Triangulation")
    print("  Calculate any polygon's area by measuring surrounding lines")
    print("=" * 60)
    print()

    sides = {}

    # Inner sides
    n_inner = int(input("How many inner sides? "))
    for i in range(n_inner):
        name = f"i{i}"
        length = float(input(f"  Length of {name}: "))
        sides[name] = {"length": length, "type": "inner"}
    print()

    # Outer sides
    n_outer = int(input("How many outer sides? "))
    for i in range(n_outer):
        name = f"o{i}"
        length = float(input(f"  Length of {name}: "))
        sides[name] = {"length": length, "type": "outer"}
    print()

    # Diagonals
    n_diag = int(input("How many diagonals? "))
    for i in range(n_diag):
        name = f"d{i}"
        length = float(input(f"  Length of {name}: "))
        sides[name] = {"length": length, "type": "diagonal"}
    print()

    # Triangles
    print("Define triangles (each has 3 sides: 2 diagonals + 1 inner or outer)")
    print(f"Available sides: {', '.join(sorted(sides.keys()))}")
    print()
    n_triangles = int(input("How many triangles? "))
    triangles = []
    for i in range(n_triangles):
        while True:
            raw = input(f"  Triangle {i} (3 side names separated by spaces): ")
            parts = raw.strip().split()
            if len(parts) != 3:
                print("    Error: enter exactly 3 side names.")
                continue
            invalid = [p for p in parts if p not in sides]
            if invalid:
                print(f"    Error: unknown side(s): {', '.join(invalid)}")
                continue
            triangles.append(parts)
            break
    print()

    # Calculate
    try:
        result = calculate_area(triangles, sides)
    except MeasurementError as e:
        print(f"ERROR: {e}")
        return

    # Display results
    print("=" * 60)
    print("  RESULTS")
    print("=" * 60)
    print()
    print("  Strategy A (coordinate reconstruction + shoelace):")
    print(f"    Inner polygon area = {result['strategy_a']:.6f}")
    print()
    print("  Strategy B (outer area - triangle areas):")
    print(f"    Outer polygon area = {result['outer_area']:.6f}")
    print(f"    Total triangle area = {result['total_triangle_area']:.6f}")
    print(f"    Inner polygon area = {result['strategy_b']:.6f}")
    print()

    diff = abs(result["strategy_a"] - result["strategy_b"])
    print(f"  Difference between strategies: {diff:.10f}")
    if diff < 1e-6:
        print("  ✓ Results match (measurements are consistent)")
    else:
        print("  ⚠ Results differ (possible measurement inaccuracy)")
    print()

    print("  Individual triangle areas:")
    for i, area in enumerate(result["triangle_areas"]):
        print(f"    Triangle {i}: {area:.6f}")
    print()


if __name__ == "__main__":
    main()
