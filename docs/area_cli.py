"""CLI interface for the area calculator via triangulation."""

# pylint: disable=too-many-locals,too-many-statements

import argparse
import sys

from area import (
    calculate_area,
    export_measurement,
    import_measurement,
    MeasurementError,
)


def display_results(result):
    """Display calculation results."""
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


def interactive_input():
    """Gather sides and triangles interactively from the user."""
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

    return sides, triangles


def do_export(sides, triangles, result, filepath):
    """Export measurement data to a JSON file."""
    name = ""
    notes = ""
    if sys.stdin.isatty():
        name = input("  Measurement name (Enter to skip): ").strip()
        notes = input("  Notes (Enter to skip): ").strip()
    json_str = export_measurement(sides, triangles, result, name=name, notes=notes)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(json_str)
    print(f"  ✓ Exported to {filepath}")
    print()


def do_import(filepath):
    """Import measurement data from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        json_str = f.read()
    data = import_measurement(json_str)

    metadata = data.get("metadata", {})
    if metadata:
        print("  Imported measurement:")
        if metadata.get("name"):
            print(f"    Name: {metadata['name']}")
        if metadata.get("date"):
            print(f"    Date: {metadata['date']}")
        if metadata.get("notes"):
            print(f"    Notes: {metadata['notes']}")
        print()

    return data["sides"], data["triangles"]


def main():
    """Run the area calculator CLI."""
    parser = argparse.ArgumentParser(description="Area Calculator via Triangulation")
    parser.add_argument(
        "--import-file",
        metavar="FILE",
        help="Import measurements from a JSON file (skips interactive input)",
    )
    parser.add_argument(
        "--export-file",
        metavar="FILE",
        help="Export measurements and results to a JSON file after calculation",
    )
    args = parser.parse_args()

    try:
        if args.import_file:
            sides, triangles = do_import(args.import_file)
        else:
            sides, triangles = interactive_input()

        result = calculate_area(triangles, sides)
        display_results(result)

        if args.export_file:
            do_export(sides, triangles, result, args.export_file)

    except MeasurementError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
