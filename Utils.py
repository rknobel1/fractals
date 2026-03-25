import Fractal_Logic as fl
import copy as _copy
from collections import deque as _deque


def reset_simulation_globals():
    """Clear module-level rule/state accumulators before a fresh run."""
    fl.states.clear()
    fl.transitions.clear()
    fl.affinities.clear()
    fl.hard_reset_tiles.clear()



def run_simulation_clean(seed_tile, stage, snapshot_cb=None):
    """Run a clean simulation without leaking previous global state."""
    reset_simulation_globals()
    return fl.run_simulation(seed_tile, stage, snapshot_cb=snapshot_cb)



def extract_tile_layout(seed_tile):
    """Traverse the assembly and return render-friendly tile metadata."""
    if seed_tile is None:
        return []

    tiles = []
    stack = _deque([(seed_tile, 0, 0)])
    visited = set()

    while stack:
        tile, x, y = stack.pop()
        if tile is None:
            continue

        ident = id(tile)
        if ident in visited:
            continue
        visited.add(ident)

        tiles.append(
            {
                "tile": tile,
                "x": x,
                "y": y,
                "status": tile.status,
                "copy_direction": tile.copy_direction,
                "pseudo_seed": bool(tile.pseudo_seed),
                "original_seed": bool(tile.original_seed),
                "wall": bool(tile.wall),
                "terminal": bool(tile.terminal),
                "caps": list(tile.caps) if tile.caps is not None else [],
                "next": list(tile.next) if tile.next is not None else [],
                "previous": list(tile.previous) if tile.previous is not None else [],
                "breadcrumbs": {"N": tile.N, "E": tile.E, "W": tile.W, "S": tile.S},
                "key_tiles": {
                    "N": tile.key_tile_N[0] if tile.key_tile_N is not None else None,
                    "E": tile.key_tile_E[0] if tile.key_tile_E is not None else None,
                    "W": tile.key_tile_W[0] if tile.key_tile_W is not None else None,
                    "S": tile.key_tile_S[0] if tile.key_tile_S is not None else None,
                },
            }
        )

        # Traverse real physical neighbors, not just logical next/previous
        if tile.tile_to_N is not None:
            stack.append((tile.tile_to_N, x, y + 1))
        if tile.tile_to_E is not None:
            stack.append((tile.tile_to_E, x + 1, y))
        if tile.tile_to_W is not None:
            stack.append((tile.tile_to_W, x - 1, y))
        if tile.tile_to_S is not None:
            stack.append((tile.tile_to_S, x, y - 1))

    return tiles



def summarize_layout(layout):
    if not layout:
        return {"tile_count": 0, "bounds": (0, 0, 0, 0), "status_counts": {}}

    xs = [item["x"] for item in layout]
    ys = [item["y"] for item in layout]
    status_counts = {}
    for item in layout:
        key = item["status"] or "None"
        status_counts[key] = status_counts.get(key, 0) + 1

    return {
        "tile_count": len(layout),
        "bounds": (min(xs), max(xs), min(ys), max(ys)),
        "status_counts": status_counts,
    }



def clone_seed(seed_tile):
    return _copy.deepcopy(seed_tile)
