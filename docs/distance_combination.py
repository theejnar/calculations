"""Find best combination of distances with gaps fitting a total length."""

# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals

from itertools import product


def find_best_combination(
    distances, from_gap, to_gap, total_length, tolerance=1e-3, gap_step=0.1
):  # pylint: disable=unused-argument
    """Find the best combination of distances and gaps to fill total_length."""
    best_result: dict | None = None
    max_counts = int(total_length // min(distances)) + 1

    for base_count in range(1, max_counts + 1):
        base_combos = product([base_count - 1, base_count], repeat=len(distances))

        for counts in base_combos:
            total_items = sum(counts)
            if total_items == 0:
                continue
            total_distance = sum(d * c for d, c in zip(distances, counts))
            num_gaps = total_items
            gap = (total_length - total_distance) / num_gaps
            if gap < from_gap - tolerance or gap > to_gap + tolerance:
                continue
            gap = max(from_gap, min(to_gap, gap))

            total_combined = total_distance + num_gaps * gap
            nonzero_counts = [c for c in counts if c > 0]
            imbalance = max(nonzero_counts) - min(nonzero_counts)
            used_dist_count = sum(1 for c in counts if c > 0)
            if (
                best_result is None
                or used_dist_count > best_result["used_count"]  # pylint: disable=unsubscriptable-object
                or (
                    used_dist_count == best_result["used_count"]  # pylint: disable=unsubscriptable-object
                    and imbalance < best_result["imbalance"]  # pylint: disable=unsubscriptable-object
                )
            ):
                best_result = {
                    "gap": round(gap, 4),
                    "total_length": round(total_combined, 4),
                    "counts": {
                        round(d, 4): c for d, c in zip(distances, counts) if c > 0
                    },
                    "imbalance": imbalance,
                    "used_count": used_dist_count,
                }

    if best_result:
        del best_result["imbalance"]
        del best_result["used_count"]
        return best_result
    return None
