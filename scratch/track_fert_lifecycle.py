import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v21_apex_sovereign_prime as s21

env = ke.make("kaggriculture", configuration={"seed": 42})
env.run([s21.agent, s21.agent])

fertilizer_collected = 0
fertilizer_used = 0
fertilizer_sold = 0

for step in range(len(env.steps) - 1):
    act = env.steps[step + 1][0].get("action", {})
    uacts = [act.get("farmer", ["PASS"])] + list(act.get("hands", []))
    for a in uacts:
        if isinstance(a, list) and len(a) > 0:
            if a[0] == "COLLECT_FERTILIZER":
                fertilizer_collected += 1
            elif a[0] == "FERTILIZE":
                fertilizer_used += 1
    
    for m in act.get("market", []):
        if len(m) >= 3 and m[0] == "SELL" and m[1] == "FERTILIZER":
            fertilizer_sold += int(m[2])

final_shed_fert = env.steps[-1][0]["observation"]["private"]["shed"].get("FERTILIZER", 0)

print(f"=== FERTILIZER LIFECYCLE (Seed 42) ===")
print(f"Collected from animals: {fertilizer_collected}")
print(f"Used to fertilize crops: {fertilizer_used}")
print(f"Sold in market:          {fertilizer_sold}")
print(f"Remaining in shed at end:{final_shed_fert}")
