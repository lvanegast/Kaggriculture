import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v21_apex_sovereign_prime as s21

env = ke.make("kaggriculture", configuration={"seed": 42})
env.run([s21.agent, s21.agent])

pass_on_fert_tile = 0
for step in range(len(env.steps) - 1):
    obs = env.steps[step][0]["observation"]
    act = env.steps[step + 1][0].get("action", {})
    farm = obs["farms"][obs["player"]]
    tiles = farm["tiles"]
    
    positions = [farm.get("farmer", [0, 0])] + list(farm.get("hands", []))
    unit_acts = [act.get("farmer", ["PASS"])] + list(act.get("hands", []))
    
    for (x, y), uact in zip(positions, unit_acts):
        t = tiles[y][x] if 0 <= y < len(tiles) and 0 <= x < len(tiles[0]) else None
        if isinstance(t, dict) and "animal" in t and t.get("fertilizer_available"):
            if uact == ["PASS"]:
                pass_on_fert_tile += 1

print(f"Turns where a worker is PASSING on an animal tile with fertilizer available: {pass_on_fert_tile}")
