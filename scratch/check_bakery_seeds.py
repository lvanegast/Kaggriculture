import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke

seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]
print("Checking unlocked shops across 10 tournament seeds:")
for s in seeds:
    env = ke.make("kaggriculture", configuration={"seed": s})
    env.reset()
    # Run 100 steps
    for _ in range(100):
        env.step([{"farmer": ["PASS"], "hands": [], "market": []}, {"farmer": ["PASS"], "hands": [], "market": []}])
    town = env.steps[-1][0]["observation"].get("town", {})
    shops = town.get("unlocked_shops", [])
    print(f"Seed {s:5d}: Unlocked shops = {shops}")
