import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v19_apex_sovereign as s19

env = ke.make("kaggriculture", configuration={"seed": 42})
env.run([s19.agent, s19.agent])

print("=== FERTILIZER & LIVESTOCK INSPECTION (Seed 42) ===")
for day in range(1, 30, 2):
    step = day * 24
    obs0 = env.steps[step][0]["observation"]
    private0 = obs0["private"]
    shed0 = private0.get("shed", {})
    fert_price = obs0.get("market", {}).get("prices", {}).get("FERTILIZER", 100)
    fert_inv = obs0.get("market", {}).get("inventory", {}).get("FERTILIZER", 10000)
    fert_shed = shed0.get("FERTILIZER", 0)
    milk_shed = shed0.get("MILK", 0)
    wool_shed = shed0.get("WOOL", 0)
    straw_shed = shed0.get("STRAWBERRY", 0)
    print(f"Day {day:2d} (Step {step:3d}): FertPrice=${fert_price} (Inv={fert_inv}) | Shed: Fert={fert_shed}, Milk={milk_shed}, Wool={wool_shed}, Straw={straw_shed}")
