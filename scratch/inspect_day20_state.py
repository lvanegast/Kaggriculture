import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v19_apex_sovereign as s19

env = ke.make("kaggriculture", configuration={"seed": 42})
env.run([s19.agent, s19.agent])

print("=== DAY 18-29 STATE INSPECTION (Seed 42) ===")
for day in [18, 20, 22, 24, 26, 28, 29]:
    step = day * 24
    obs0 = env.steps[step][0]["observation"]
    farm0 = obs0["farms"][0]
    private0 = obs0["private"]
    shed0 = private0.get("shed", {})
    money0 = farm0.get("money", 0)
    hands0 = len(farm0.get("hands", []))
    market_wheat_price = obs0.get("market", {}).get("prices", {}).get("WHEAT", 25)
    market_wheat_inv = obs0.get("market", {}).get("inventory", {}).get("WHEAT", 10000)
    
    # Count tiles
    tiles = farm0.get("tiles", [])
    crop_counts = {}
    animal_counts = {}
    empty_tiles = 0
    weed_tiles = 0
    locked_tiles = 0
    for r in tiles:
        for t in r:
            if t == "LOCKED":
                locked_tiles += 1
            elif t is None:
                empty_tiles += 1
            elif isinstance(t, dict):
                if t.get("kind") == "WEED":
                    weed_tiles += 1
                if "crop" in t:
                    c = t["crop"]
                    crop_counts[c] = crop_counts.get(c, 0) + 1
                if "animal" in t:
                    a = t["animal"]
                    animal_counts[a] = animal_counts.get(a, 0) + 1

    print(f"Day {day:2d} (Step {step:3d}): Money=${money0:7.0f} | Hands={hands0} | WheatPrice=${market_wheat_price} (Inv={market_wheat_inv}) | ShedWheat={shed0.get('WHEAT', 0)}")
    print(f"   Crops: {crop_counts} | Animals: {animal_counts} | Empty={empty_tiles} | Weeds={weed_tiles}")
