import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v16_apex_titan as s16

def opportunistic_dig(obs, action):
    seat = s16._seat_guard(obs)
    farm = s16._farm_guard(obs, seat)
    tiles = farm.get("tiles", [])
    
    # Check farmer
    farmer = list(action.get("farmer", ["PASS"]))
    if farmer == ["PASS"] and "farmer" in farm:
        fx, fy = farm["farmer"]
        tile = tiles[fy][fx] if 0 <= fy < len(tiles) and 0 <= fx < len(tiles[0]) else None
        if isinstance(tile, dict) and bool(tile.get("weed")):
            farmer = ["DIG"]
            
    # Check hands
    hands = [list(h) for h in action.get("hands", [])]
    hand_positions = farm.get("hands", [])
    for idx, pos in enumerate(hand_positions):
        if idx < len(hands) and hands[idx] == ["PASS"]:
            hx, hy = pos
            tile = tiles[hy][hx] if 0 <= hy < len(tiles) and 0 <= hx < len(tiles[0]) else None
            if isinstance(tile, dict) and bool(tile.get("weed")):
                hands[idx] = ["DIG"]
                
    action["farmer"] = farmer
    action["hands"] = hands
    return action

def agent_v17(obs, config=None):
    step = int(s16._v43_get(obs, "step", 0) or 0)
    act = s16._V43_POLICY(obs, config)
    act = opportunistic_dig(obs, act)
    act = s16._capital_guard(obs, act, step)
    act = s16._terminal_zero_waste_sweep(obs, act, step)
    return s16._align_hands(act, obs)

seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]
scores = []
print("Evaluating v17 with Opportunistic DIG across 10 seeds...")
for s in seeds:
    env = ke.make("kaggriculture", configuration={"seed": s})
    env.run([agent_v17, agent_v17])
    s0 = env.steps[-1][0]["reward"]
    s1 = env.steps[-1][1]["reward"]
    scores.append((s0 + s1) / 2)
    print(f"Seed {s:5d}: P0=${s0:8.0f} | P1=${s1:8.0f}")

print(f"\nAverage: ${sum(scores)/len(scores):8.1f}")
