import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import kaggle_environments as ke
import submission_v16_apex_titan as s16

seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]
for s in seeds:
    env = ke.make("kaggriculture", configuration={"seed": s})
    env.reset()
    for _ in range(250):
        env.step([{"farmer": ["PASS"], "hands": [], "market": []}, {"farmer": ["PASS"], "hands": [], "market": []}])
    town = env.state[0]["observation"]["town"]
    shops = town.get("unlocked_shops", [])
    print(f"Seed {s:5d}: Unlocked shops by step 250: {shops}")
