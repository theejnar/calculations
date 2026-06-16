"""CLI interface for the distance combination calculator."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from distance_combination import find_best_combination  # noqa: E402  # pylint: disable=wrong-import-position


def main():  # pylint: disable=too-many-locals
    """Run the distance combination calculator CLI."""
    parser = argparse.ArgumentParser(
        description="Find the best combination of distances with gaps fitting a total length."
    )
    parser.add_argument("--file", "-f", type=str, help="Path to a JSON settings file")
    parser.add_argument(
        "--distances",
        "-d",
        type=str,
        help="Space-separated distances (e.g. '70 95 120')",
    )
    parser.add_argument("--from-gap", type=float, help="Minimum gap")
    parser.add_argument("--to-gap", type=float, help="Maximum gap")
    parser.add_argument("--total-length", type=float, help="Target total length")
    parser.add_argument("--tolerance", type=float, default=0.001)
    parser.add_argument("--gap-step", type=float, default=0.1)
    parser.add_argument(
        "--export",
        "-e",
        type=str,
        help="Export settings to a JSON file (no calculation)",
    )

    args = parser.parse_args()

    # Load from file if provided
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            data = json.load(f)
        distances_str = data.get("distances", "")
        from_gap = data.get("from_gap", args.from_gap)
        to_gap = data.get("to_gap", args.to_gap)
        total_length = data.get("total_length", args.total_length)
        tolerance = data.get("tolerance", args.tolerance)
        gap_step = data.get("gap_step", args.gap_step)
    else:
        distances_str = args.distances
        from_gap = args.from_gap
        to_gap = args.to_gap
        total_length = args.total_length
        tolerance = args.tolerance
        gap_step = args.gap_step

    if not distances_str or from_gap is None or to_gap is None or total_length is None:
        parser.error(
            "Either --file or all of --distances, --from-gap,"
            " --to-gap, --total-length are required."
        )

    distances = [float(x) for x in distances_str.split()]

    # Export mode
    if args.export:
        settings = {
            "distances": distances_str,
            "from_gap": from_gap,
            "to_gap": to_gap,
            "total_length": total_length,
            "tolerance": tolerance,
            "gap_step": gap_step,
        }
        with open(args.export, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        print(f"Settings exported to {args.export}")
        return

    # Calculate
    result = find_best_combination(
        distances,
        from_gap,
        to_gap,
        total_length,
        tolerance=tolerance,
        gap_step=gap_step,
    )

    if result is None:
        print("No suitable combination found.")
        sys.exit(1)

    print("=" * 50)
    print("  RESULT")
    print("=" * 50)
    print()
    print(f"  Gap: {result['gap']}")
    print(f"  Total length achieved: {result['total_length']}")
    print()
    for dist, count in result["counts"].items():
        print(f"  Distance {dist}: x {count}")
    print()


if __name__ == "__main__":
    main()
