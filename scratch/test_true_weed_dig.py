import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v17_apex_colossus as s17

def _true_opportunistic_weed_dig(obs, action):
    seat = s17._seat_guard(obs)
    farm = s17._farm_guard(obs, seat)
    tiles = farm.get("tiles", [])
    if not tiles:
        return action
        
    farmer = list(action.get("farmer", ["PASS"]))
    if farmer == ["PASS"] and "farmer" in farm:
        fx, fy = farm["farmer"]
        tile = tiles[fy][fx] if 0 <= fy < len(tiles) and 0 <= fx < len(tiles[0]) else None
        if isinstance(tile, dict) and (tile.get("kind") == "WEED" or bool(tile.get("weed"))):
            farmer = ["DIG"]
            
    hands = [list(h) for h in action.get("hands", [])]
    hand_positions = farm.get("hands", [])
    for idx, pos in enumerate(hand_positions):
        if idx < len(hands) and hands[idx] == ["PASS"]:
            hx, hy = pos
            tile = tiles[hy][hx] if 0 <= hy < len(tiles) and 0 <= hx < len(tiles[0]) else None
            if isinstance(tile, dict) and (tile.get("kind") == "WEED" or bool(tile.get("weed"))):
                hands[idx] = ["DIG"]
                
    action["farmer"] = farmer
    action["hands"] = hands
    return action

def agent_true_dig(obs, config=None):
    step = int(s17._v43_get(obs, "step", 0) or 0)
    act = s17._V43_POLICY(obs, config)
    act = _true_opportunistic_weed_dig(obs, act)
    act = s17._capital_guard(obs, act, step)
    act = s17._terminal_zero_waste_sweep(obs, act, step)
    return s17._align_hands(act, obs)

seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]
scores = []
print("Evaluating agent_true_dig across 10 seeds...", flush=True)
for s in seeds:
    env = ke.make("kaggriculture", configuration={"seed": s})
    env.run([agent_true_dig, agent_true_dig])
    s0 = env.steps[-1][0]["reward"]
    s1 = env.steps[-1][1]["reward"]
    scores.append((s0 + s1) / 2)
    print(f"Seed {s:5d}: P0=${s0:8.0f} | P1=${s1:8.0f} | Avg=${(s0+s1)/2:8.0f}", flush=True)

print(f"\nOverall Average: ${sum(scores)/len(scores):8.1f}", flush=True)
