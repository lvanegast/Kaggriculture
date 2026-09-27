import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v21_apex_sovereign_prime as s21

bad_seeds = [7, 555, 2024, 888]
good_seeds = [42, 1234]

for s in bad_seeds + good_seeds:
    env = ke.make("kaggriculture", configuration={"seed": s})
    env.run([s21.agent, s21.agent])
    obs = env.steps[-1][0]["observation"]
    farm = obs["farms"][obs["player"]]
    money = farm["money"]
    town = obs.get("town", {})
    shops = town.get("unlocked_shops", [])
    
    # Count animals alive at end
    cows = sum(1 for row in farm["tiles"] for t in row if isinstance(t, dict) and t.get("animal") == "COW")
    sheep = sum(1 for row in farm["tiles"] for t in row if isinstance(t, dict) and t.get("animal") == "SHEEP")
    weeds = sum(1 for row in farm["tiles"] for t in row if isinstance(t, dict) and t.get("kind") == "WEED")
    quads = len(farm.get("unlocked_quadrants", []))
    
    print(f"Seed {s:5d}: Money=${money:8.0f} | Shops={shops} | Cows={cows}, Sheep={sheep} | Weeds={weeds} | Quads={quads}")
