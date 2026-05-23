"""Calculate polygon area via surrounding triangle measurements."""

# pylint: disable=too-many-locals,too-many-branches,too-many-statements
# pylint: disable=too-many-nested-blocks

import math
from collections import deque


class MeasurementError(Exception):
    """Raised when measurements are geometrically inconsistent."""


def herons_area(a, b, c):
    """Compute triangle area from three side lengths using Heron's formula."""
    s = (a + b + c) / 2
    val = s * (s - a) * (s - b) * (s - c)
    if val < 0:
        return 0.0
    return math.sqrt(val)


def validate_triangle(side_a, side_b, side_c, triangle_name=""):
    """Check triangle inequality. Raises MeasurementError if violated."""
    sides = sorted([(side_a, "a"), (side_b, "b"), (side_c, "c")])
    lengths = [s[0] for s in sides]
    if lengths[0] + lengths[1] <= lengths[2]:
        msg = (
            f"Triangle inequality violated"
            f"{' in ' + triangle_name if triangle_name else ''}: "
            f"sides {lengths[0]:.4f} + {lengths[1]:.4f} = {lengths[0] + lengths[1]:.4f} "
            f"<= {lengths[2]:.4f}. "
            f"The longest side ({lengths[2]:.4f}) is likely measured incorrectly."
        )
        raise MeasurementError(msg)


def suggest_triangles(sides):
    """Suggest triangle definitions based on the standard ring pattern.

    For n inner sides and n outer sides with 2n diagonals, produces 2n triangles:
    - n inner triangles: each uses 1 inner side + 2 adjacent diagonals
    - n outer triangles: each uses 1 outer side + 2 adjacent diagonals

    Returns a list of [side1, side2, side3] lists.
    """
    inner_names = sorted(
        [k for k, v in sides.items() if v["type"] == "inner"], key=lambda x: int(x[1:])
    )
    outer_names = sorted(
        [k for k, v in sides.items() if v["type"] == "outer"], key=lambda x: int(x[1:])
    )
    diag_names = sorted(
        [k for k, v in sides.items() if v["type"] == "diagonal"],
        key=lambda x: int(x[1:]),
    )

    n = len(inner_names)
    if n == 0:
        raise MeasurementError("No inner sides defined.")
    if len(outer_names) != n:
        raise MeasurementError(
            f"Expected {n} outer sides to match {n} inner sides, got {len(outer_names)}."
        )
    if len(diag_names) != 2 * n:
        raise MeasurementError(
            f"Expected {2 * n} diagonals for {n} inner sides, got {len(diag_names)}."
        )

    triangles = []
    for i in range(n):
        # Inner triangle: inner_i + diag_{2i} + diag_{2i+1}
        triangles.append([inner_names[i], diag_names[2 * i], diag_names[2 * i + 1]])
    for i in range(n):
        # Outer triangle: outer_i + diag_{2i+1} + diag_{(2i+2) mod 2n}
        triangles.append(
            [outer_names[i], diag_names[2 * i + 1], diag_names[(2 * i + 2) % (2 * n)]]
        )

    return triangles


def validate_connectivity(triangles, _sides):
    """Verify all triangles form a connected graph via shared sides."""
    if not triangles:
        raise MeasurementError("No triangles defined.")

    # Build adjacency: two triangles are adjacent if they share a side
    adj = {i: set() for i in range(len(triangles))}
    side_to_triangles = {}
    for i, tri in enumerate(triangles):
        for side_name in tri:
            if side_name not in side_to_triangles:
                side_to_triangles[side_name] = []
            side_to_triangles[side_name].append(i)

    for tri_indices in side_to_triangles.values():
        for i, ti in enumerate(tri_indices):
            for tj in tri_indices[i + 1 :]:
                adj[ti].add(tj)
                adj[tj].add(ti)

    # BFS from triangle 0
    visited = set()
    queue = deque([0])
    visited.add(0)
    while queue:
        node = queue.popleft()
        for neighbor in adj[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    if len(visited) != len(triangles):
        unreachable = set(range(len(triangles))) - visited
        raise MeasurementError(
            f"Triangles are not fully connected. "
            f"Disconnected triangle indices: {sorted(unreachable)}"
        )


def reconstruct_coordinates(triangles, sides):
    """
    Reconstruct 2D vertex coordinates from triangle side lengths.

    Uses BFS placement. For each new triangle adjacent to a placed one via a
    shared side, tries both possible vertex assignments and picks the one
    consistent with other already-placed neighbors.

    Returns:
        vertices: dict mapping vertex_id -> (x, y)
        tri_vertex_ids: list of (v0_id, v1_id, v2_id) for each triangle
        inner_loop: list of vertex_ids forming the inner polygon (ordered)
        outer_loop: list of vertex_ids forming the outer polygon (ordered)
    """
    if not triangles:
        raise MeasurementError("No triangles to reconstruct.")

    n = len(triangles)
    tri_sides = []
    for i, tri in enumerate(triangles):
        side_names = list(tri)
        lengths = [sides[s]["length"] for s in side_names]
        tri_sides.append({"names": side_names, "lengths": lengths})

    # Build side-to-triangles mapping
    side_to_tris = {}
    for i, tri in enumerate(triangles):
        for s in tri:
            side_to_tris.setdefault(s, []).append(i)

    # Coordinate-based reconstruction
    epsilon = 1e-4
    coords = {}  # global_vertex_id -> (x, y)
    next_vid = [0]
    tri_vertex_ids = [None] * n
    placed = [False] * n

    def find_or_create_vertex(x, y):
        """Find existing vertex at (x,y) or create a new one."""
        for vid, (vx, vy) in coords.items():
            if abs(vx - x) < epsilon and abs(vy - y) < epsilon:
                return vid
        vid = next_vid[0]
        next_vid[0] += 1
        coords[vid] = (x, y)
        return vid

    def check_neighbor_consistency(tj, new_pos, va_id, vb_id, idx_j):
        """
        Check if placing the new vertex at new_pos with the given assignment
        is consistent with other already-placed triangles that share sides
        with tj.
        """
        # Build the proposed vertex assignment for tj
        prop_vids = [None, None, None]
        prop_vids[idx_j] = new_pos  # (x,y) tuple for the new vertex
        prop_vids[(idx_j + 1) % 3] = va_id
        prop_vids[(idx_j + 2) % 3] = vb_id

        score = 0  # number of consistent checks

        # For each OTHER side of tj (not the shared one we came from):
        for local_side_idx in range(3):
            if local_side_idx == idx_j:
                continue  # this is the shared side we came from
            other_side_name = tri_sides[tj]["names"][local_side_idx]
            other_tris = side_to_tris.get(other_side_name, [])
            for tk in other_tris:
                if tk == tj or not placed[tk]:
                    continue
                # tk is placed and shares other_side_name with tj
                # This side connects local vertices (local_side_idx+1)%3
                # and (local_side_idx+2)%3 in tj
                v_end1_idx = (local_side_idx + 1) % 3
                v_end2_idx = (local_side_idx + 2) % 3

                # Get the coords of these endpoints in our proposed assignment
                def get_pos(local_idx):
                    if local_idx == idx_j:
                        return new_pos
                    vid = prop_vids[local_idx]
                    return coords[vid]

                pos1 = get_pos(v_end1_idx)
                pos2 = get_pos(v_end2_idx)

                # Find the side's index in tk
                idx_k = tri_sides[tk]["names"].index(other_side_name)
                # This side in tk connects vertices (idx_k+1)%3 and (idx_k+2)%3
                tk_v1_id = tri_vertex_ids[tk][(idx_k + 1) % 3]
                tk_v2_id = tri_vertex_ids[tk][(idx_k + 2) % 3]
                tk_pos1 = coords[tk_v1_id]
                tk_pos2 = coords[tk_v2_id]

                # Check if (pos1,pos2) matches (tk_pos1,tk_pos2) in either order
                d11 = math.sqrt(
                    (pos1[0] - tk_pos1[0]) ** 2 + (pos1[1] - tk_pos1[1]) ** 2
                )
                d12 = math.sqrt(
                    (pos1[0] - tk_pos2[0]) ** 2 + (pos1[1] - tk_pos2[1]) ** 2
                )
                d21 = math.sqrt(
                    (pos2[0] - tk_pos1[0]) ** 2 + (pos2[1] - tk_pos1[1]) ** 2
                )
                d22 = math.sqrt(
                    (pos2[0] - tk_pos2[0]) ** 2 + (pos2[1] - tk_pos2[1]) ** 2
                )

                if (d11 < epsilon and d22 < epsilon) or (
                    d12 < epsilon and d21 < epsilon
                ):
                    score += 1
                else:
                    return -1  # inconsistent
        return score

    # Place first triangle at origin
    a = tri_sides[0]["lengths"][2]  # v0-v1 distance (side 2 opposite v2)
    b = tri_sides[0]["lengths"][1]  # v0-v2 distance (side 1 opposite v1)
    c = tri_sides[0]["lengths"][0]  # v1-v2 distance (side 0 opposite v0)

    v0 = find_or_create_vertex(0.0, 0.0)
    v1 = find_or_create_vertex(a, 0.0)
    x2, y2 = _third_point((0, 0), (a, 0), b, c)
    v2 = find_or_create_vertex(x2, y2)
    tri_vertex_ids[0] = (v0, v1, v2)
    placed[0] = True

    # Iterative placement: keep trying unplaced triangles until all are placed.
    # Prefer triangles with more placed neighbors (better disambiguation).
    # Defer triangles with score=0 for both assignments (ambiguous).
    max_iterations = n * n
    iteration = 0
    while not all(placed) and iteration < max_iterations:
        iteration += 1
        progress = False

        # Gather all placeable candidates: unplaced triangles adjacent to placed ones
        candidates = []
        for tj in range(n):
            if placed[tj]:
                continue
            # Find placed neighbor(s) for this triangle
            best_ti = None
            best_side = None
            placed_count = 0
            for s in tri_sides[tj]["names"]:
                for tk in side_to_tris.get(s, []):
                    if tk != tj and placed[tk]:
                        placed_count += 1
                        if best_ti is None:
                            best_ti = tk
                            best_side = s
            if best_ti is not None:
                candidates.append((tj, best_ti, best_side, placed_count))

        # Sort by most placed neighbors first
        candidates.sort(key=lambda x: -x[3])

        for tj, ti, side_name, _ in candidates:
            if placed[tj]:
                continue

            # Find shared side index in both triangles
            idx_i = tri_sides[ti]["names"].index(side_name)
            idx_j = tri_sides[tj]["names"].index(side_name)

            # The two vertices of the shared edge (from the placed triangle ti)
            shared_va_id = tri_vertex_ids[ti][(idx_i + 1) % 3]
            shared_vb_id = tri_vertex_ids[ti][(idx_i + 2) % 3]
            pa = coords[shared_va_id]
            pb = coords[shared_vb_id]

            # The opposite point from ti
            ti_third_id = tri_vertex_ids[ti][idx_i]
            ti_third_pos = coords[ti_third_id]

            # Assignment 1: local (idx_j+1)%3 = va, local (idx_j+2)%3 = vb
            d_new_pa_1 = tri_sides[tj]["lengths"][(idx_j + 2) % 3]
            d_new_pb_1 = tri_sides[tj]["lengths"][(idx_j + 1) % 3]

            # Assignment 2: local (idx_j+1)%3 = vb, local (idx_j+2)%3 = va
            d_new_pa_2 = tri_sides[tj]["lengths"][(idx_j + 1) % 3]
            d_new_pb_2 = tri_sides[tj]["lengths"][(idx_j + 2) % 3]

            # Compute new vertex position for each assignment
            pos1 = _third_point_opposite(pa, pb, d_new_pa_1, d_new_pb_1, ti_third_pos)
            pos2 = _third_point_opposite(pa, pb, d_new_pa_2, d_new_pb_2, ti_third_pos)

            # Check consistency with other placed neighbors
            score1 = check_neighbor_consistency(
                tj, pos1, shared_va_id, shared_vb_id, idx_j
            )
            score2 = check_neighbor_consistency(
                tj, pos2, shared_vb_id, shared_va_id, idx_j
            )

            # If both scores are 0 and no disambiguation possible, defer
            if (
                score1 == 0
                and score2 == 0
                and not all(placed[k] for k in range(n) if k != tj)
            ):
                # Check if there are other unplaced candidates with better context
                has_better = any(
                    c[3] > 1 for c in candidates if not placed[c[0]] and c[0] != tj
                )
                if has_better:
                    continue  # defer this one

            if score2 > score1:
                new_vid = find_or_create_vertex(*pos2)
                vids = [None, None, None]
                vids[idx_j] = new_vid
                vids[(idx_j + 1) % 3] = shared_vb_id
                vids[(idx_j + 2) % 3] = shared_va_id
            else:
                new_vid = find_or_create_vertex(*pos1)
                vids = [None, None, None]
                vids[idx_j] = new_vid
                vids[(idx_j + 1) % 3] = shared_va_id
                vids[(idx_j + 2) % 3] = shared_vb_id

            tri_vertex_ids[tj] = tuple(vids)
            placed[tj] = True
            progress = True

        if not progress:
            # Force-place the first available candidate to break deadlock
            for tj, ti, side_name, _ in candidates:
                if not placed[tj]:
                    idx_i = tri_sides[ti]["names"].index(side_name)
                    idx_j = tri_sides[tj]["names"].index(side_name)
                    shared_va_id = tri_vertex_ids[ti][(idx_i + 1) % 3]
                    shared_vb_id = tri_vertex_ids[ti][(idx_i + 2) % 3]
                    pa = coords[shared_va_id]
                    pb = coords[shared_vb_id]
                    ti_third_id = tri_vertex_ids[ti][idx_i]
                    ti_third_pos = coords[ti_third_id]

                    d_new_pa_1 = tri_sides[tj]["lengths"][(idx_j + 2) % 3]
                    d_new_pb_1 = tri_sides[tj]["lengths"][(idx_j + 1) % 3]
                    pos1 = _third_point_opposite(
                        pa, pb, d_new_pa_1, d_new_pb_1, ti_third_pos
                    )

                    new_vid = find_or_create_vertex(*pos1)
                    vids = [None, None, None]
                    vids[idx_j] = new_vid
                    vids[(idx_j + 1) % 3] = shared_va_id
                    vids[(idx_j + 2) % 3] = shared_vb_id
                    tri_vertex_ids[tj] = tuple(vids)
                    placed[tj] = True
                    progress = True
                    break

            if not progress:
                break

    if not all(placed):
        unplaced = [i for i, p in enumerate(placed) if not p]
        raise MeasurementError(
            f"Could not place all triangles. Unplaced: {unplaced}. "
            f"Check that triangles share sides correctly."
        )

    # Identify inner and outer polygon vertex loops
    inner_loop = _extract_loop(triangles, sides, tri_vertex_ids, tri_sides, "inner")
    outer_loop = _extract_loop(triangles, sides, tri_vertex_ids, tri_sides, "outer")

    return coords, tri_vertex_ids, inner_loop, outer_loop


def _third_point(p1, p2, d1, d2):
    """
    Find a point at distance d1 from p1 and d2 from p2.
    Returns the point with positive y (above the line p1-p2).
    """
    ax, ay = p1
    bx, by = p2
    d = math.sqrt((bx - ax) ** 2 + (by - ay) ** 2)
    if d < 1e-12:
        raise MeasurementError("Two vertices at the same position.")
    # Using the formula for circle-circle intersection
    a_val = (d1 * d1 - d2 * d2 + d * d) / (2 * d)
    h_sq = max(d1 * d1 - a_val * a_val, 0)
    h = math.sqrt(h_sq)
    # Direction vector from p1 to p2
    dx = (bx - ax) / d
    dy = (by - ay) / d
    # Midpoint along the line
    mx = ax + a_val * dx
    my = ay + a_val * dy
    # Perpendicular
    x = mx + h * (-dy)
    y = my + h * dx
    return (x, y)


def _third_point_opposite(p1, p2, d1, d2, opposite_to):
    """
    Find a point at distance d1 from p1 and d2 from p2,
    on the opposite side of line p1-p2 from opposite_to.
    """
    ax, ay = p1
    bx, by = p2
    d = math.sqrt((bx - ax) ** 2 + (by - ay) ** 2)
    if d < 1e-12:
        raise MeasurementError("Two vertices at the same position.")
    a_val = (d1 * d1 - d2 * d2 + d * d) / (2 * d)
    h_sq = max(d1 * d1 - a_val * a_val, 0)
    h = math.sqrt(h_sq)
    dx = (bx - ax) / d
    dy = (by - ay) / d
    mx = ax + a_val * dx
    my = ay + a_val * dy
    # Two candidate points
    cx1 = mx + h * (-dy)
    cy1 = my + h * dx
    cx2 = mx - h * (-dy)
    cy2 = my - h * dx

    # Determine which side opposite_to is on
    # Cross product of (p2-p1) x (opposite_to-p1)
    cross_ref = (bx - ax) * (opposite_to[1] - ay) - (by - ay) * (opposite_to[0] - ax)
    cross_c1 = (bx - ax) * (cy1 - ay) - (by - ay) * (cx1 - ax)

    # Pick the point on the opposite side
    if cross_ref * cross_c1 <= 0:
        return (cx1, cy1)
    return (cx2, cy2)


def _extract_loop(triangles, sides, tri_vertex_ids, _tri_sides, side_type):
    """
    Extract an ordered loop of vertex IDs connected by sides of the given type.
    """
    # Find all sides of this type and their vertex pairs
    edges = []
    for side_name, info in sides.items():
        if info["type"] != side_type:
            continue
        # Find which triangle contains this side and get vertex IDs
        for i, tri in enumerate(triangles):
            tri_side_names = list(tri)
            if side_name in tri_side_names:
                idx = tri_side_names.index(side_name)
                v1 = tri_vertex_ids[i][(idx + 1) % 3]
                v2 = tri_vertex_ids[i][(idx + 2) % 3]
                edges.append((v1, v2, side_name))
                break

    if not edges:
        return []

    # Build adjacency
    adj = {}
    for v1, v2, sname in edges:
        adj.setdefault(v1, []).append((v2, sname))
        adj.setdefault(v2, []).append((v1, sname))

    # Traverse — find the longest path (may or may not close into a loop)
    # Try starting from a vertex with degree 1 (endpoint) if any,
    # otherwise start from the first edge vertex
    start = None
    for v, neighbors in adj.items():
        if len(neighbors) == 1:
            start = v
            break
    if start is None:
        start = edges[0][0]

    loop = [start]
    prev = None
    current = start
    for _ in range(len(edges)):
        neighbors = adj[current]
        next_v = None
        for nb, sname in neighbors:
            if nb != prev:
                next_v = nb
                break
        if next_v is None or next_v == start:
            break
        loop.append(next_v)
        prev = current
        current = next_v

    return loop


def shoelace_area(coords, vertex_loop):
    """Compute polygon area using the shoelace formula on ordered vertices."""
    n = len(vertex_loop)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        xi, yi = coords[vertex_loop[i]]
        xj, yj = coords[vertex_loop[j]]
        area += xi * yj - xj * yi
    return abs(area) / 2.0


def calculate_area(triangles, sides):
    """
    Calculate the inner polygon area using both strategies.

    Args:
        triangles: list of lists/tuples, each containing 3 side names
        sides: dict mapping side_name -> {"length": float, "type": "inner"|"outer"|"diagonal"}

    Returns:
        dict with keys:
            "strategy_a": area from direct shoelace on inner polygon
            "strategy_b": area from outer shoelace minus Heron's triangle sum
            "triangle_areas": list of individual triangle areas
            "total_triangle_area": sum of all triangle areas
            "outer_area": outer polygon area
            "coords": vertex coordinates dict
            "inner_loop": ordered inner vertex IDs
            "outer_loop": ordered outer vertex IDs
            "tri_vertex_ids": vertex IDs per triangle
    """
    # Validate all triangles
    for i, tri in enumerate(triangles):
        side_names = list(tri)
        lengths = [sides[s]["length"] for s in side_names]
        validate_triangle(lengths[0], lengths[1], lengths[2], f"T{i} ({side_names})")

    # Validate connectivity
    validate_connectivity(triangles, sides)

    # Reconstruct coordinates
    coords, tri_vertex_ids, inner_loop, outer_loop = reconstruct_coordinates(
        triangles, sides
    )

    warnings = []
    if len(inner_loop) < 3:
        warnings.append(
            "Inner sides do not form a complete polygon "
            f"(found {len(inner_loop)} vertices). Area may be inaccurate."
        )
    if len(outer_loop) < 3:
        warnings.append(
            "Outer sides do not form a complete polygon "
            f"(found {len(outer_loop)} vertices). Area may be inaccurate."
        )

    # Strategy A: Shoelace on inner polygon
    area_a = shoelace_area(coords, inner_loop)

    # Strategy B: Outer area minus triangle areas
    area_outer = shoelace_area(coords, outer_loop)
    triangle_areas = []
    for i, tri in enumerate(triangles):
        lengths = [sides[s]["length"] for s in tri]
        triangle_areas.append(herons_area(*lengths))
    total_tri_area = sum(triangle_areas)
    area_b = area_outer - total_tri_area

    return {
        "strategy_a": area_a,
        "strategy_b": area_b,
        "triangle_areas": triangle_areas,
        "total_triangle_area": total_tri_area,
        "outer_area": area_outer,
        "coords": coords,
        "inner_loop": inner_loop,
        "outer_loop": outer_loop,
        "tri_vertex_ids": tri_vertex_ids,
        "warnings": warnings,
    }
