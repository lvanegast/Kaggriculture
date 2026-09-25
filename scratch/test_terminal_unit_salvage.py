import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v17_apex_colossus as s17

def _move_toward(position, targets, tiles):
    x, y = position
    if not targets:
        return ["PASS"]
    target = min(targets, key=lambda point: (abs(point[0] - x) + abs(point[1] - y), point[1], point[0]))
    tx, ty = target
    candidates = []
    if tx < x:
        candidates.append(("WEST", x - 1, y))
    if tx > x:
        candidates.append(("EAST", x + 1, y))
    if ty < y:
        candidates.append(("NORTH", x, y - 1))
    if ty > y:
        candidates.append(("SOUTH", x, y + 1))
    size = len(tiles)
    for operation, nx, ny in candidates:
        if 0 <= nx < size and 0 <= ny < size and tiles[ny][nx] != "LOCKED":
            return [operation]
    return ["PASS"]

def monetizable_terminal_units(obs, action, step):
    action = s17._align_hands(action, obs)
    if step not in (717, 718):
        return action
    player = s17._seat_guard(obs)
    farm = s17._farm_guard(obs, player)
    private = obs.get("private", {}) or {}
    tiles = farm.get("tiles", []) or []
    if not tiles:
        return action
    half = len(tiles) // 2
    access = {(half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half)}
    positions = [farm.get("farmer", [0, 0]), *(farm.get("hands", []) or [])]
    inventories = list(private.get("inventories", []) or [])
    inventories.extend({} for _ in range(max(0, len(positions) - len(inventories))))
    unit_actions = [action.get("farmer", ["PASS"]), *(action.get("hands") or [])]

    for index, (raw_position, inventory) in enumerate(zip(positions, inventories)):
        if not isinstance(raw_position, (list, tuple)) or len(raw_position) < 2:
            continue
        position = (int(raw_position[0]), int(raw_position[1]))
        load = sum(max(0, int(value or 0)) for value in (inventory or {}).values())
        x, y = position
        tile = tiles[y][x] if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]) else None
        distance = min(abs(x - sx) + abs(y - sy) for sx, sy in access)
        replacement = None
        if load > 0 and position in access:
            replacement = ["DROP"]
        elif step == 717 and load > 0 and distance == 1:
            replacement = _move_toward(position, access, tiles)
        elif (
            step == 717
            and load == 0
            and position in access
            and isinstance(tile, dict)
            and int(tile.get("yield_units", 0) or 0) > 0
        ):
            replacement = ["HARVEST"]
        if replacement is not None:
            unit_actions[index] = replacement

    action["farmer"] = unit_actions[0]
    action["hands"] = unit_actions[1:]
    return action

def agent_salvage(obs, config=None):
    step = int(s17._v43_get(obs, "step", 0) or 0)
    act = s17._V43_POLICY(obs, config)
    act = s17._opportunistic_weed_dig(obs, act)
    act = s17._capital_guard(obs, act, step)
    act = monetizable_terminal_units(obs, act, step)
    act = s17._terminal_zero_waste_sweep(obs, act, step)
    return s17._align_hands(act, obs)

seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]
scores = []
print("Evaluating agent_salvage across 10 seeds...", flush=True)
for s in seeds:
    env = ke.make("kaggriculture", configuration={"seed": s})
    env.run([agent_salvage, agent_salvage])
    s0 = env.steps[-1][0]["reward"]
    s1 = env.steps[-1][1]["reward"]
    scores.append((s0 + s1) / 2)
    print(f"Seed {s:5d}: P0=${s0:8.0f} | P1=${s1:8.0f} | Avg=${(s0+s1)/2:8.0f}", flush=True)

print(f"\nOverall Average: ${sum(scores)/len(scores):8.1f}", flush=True)
